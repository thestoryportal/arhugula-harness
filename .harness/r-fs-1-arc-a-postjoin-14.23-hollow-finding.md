# R-FS-1 arc-a `B-POSTJOIN-LLM-SYNTHESIS` — OPTION-B §14.23 cached-replay capture is a write-only (hollow) carrier

*Process-substrate finding (mode-agnostic; no design-substrate / src edit). Surfaced at arc-a spec-amendment grounding, 2026-06-22→23 loop session. Discipline anchors: `[[full-chain-witness-not-half-proofs]]`, `[[grounding-reveals-claude-closeable-slice-close-honestly]]`, `[[feedback-gate-only-on-meaningful-architecture-change]]`, the #705 hollow-carrier resolution (`B-INTERSTEP-NONLINEAR` RESOLVED-AS-HOLLOW). advisor (transcript-aware) + a code-grounded Explore trace both converge.*

## What the operator ratified (2026-06-22)

Arc-a AUQ: the operator chose **OPTION B** ("Build cached-replay now") over the council-**recommended OPTION A** ("accept the forward-looking residual + register reproducible cached-replay as a follow-on; the divergence window is currently empty"). OPTION B = *gate synthesis to replay-capable engine classes (`EVENT_SOURCED_REPLAY`/`WAL_SEGMENT`) + build the §14.23 cached-replay capture up front (extend `EngineOutputStore`/a sibling store to capture the driver-level synthesis output)*, "closing the currently-empty forward divergence window at build time."

## The empirical finding (grounded against HEAD `2dcd488`)

**OPTION B's §14.23 capture, as literally scoped ("capture the driver-level synthesis output"), produces a producer with NO consumer in the wired harness — the exact #705 hollow-carrier pattern, one level up.**

Evidence (advisor + Explore trace of `harness-cp/src/harness_cp/workflow_driver.py` + `harness-runtime/.../lifecycle/engine_output_store.py`):

1. **The post-join synthesis is TERMINAL.** The fan-out aggregate is a driver-level fold (`drain_branch_buffers:878` + `_aggregate_orchestrator_workers`/`_aggregate_parallelization`) computed ONCE at the barrier drain → packaged directly into `RunResult.final_state` (`:380`, `:3892`). Completing the synthesis = completing the run. There is no "re-reach a completed terminal synthesis" state in a crash-resume model: either the synthesis returned (run done, nothing to resume to) or it didn't (nothing captured).
2. **Fan-out crash-resume never re-reaches the post-barrier dispatch (Q1: NO).** Non-linear strategies early-return from `_execute_workflow_body` (`:1660-1758`) and never fall through to the linear loop; fan-out resume (`fan_out_resume`/`peer_fan_out_resume`, `:1593-1718`) is **branch-scoped** (skip completed branches, re-dispatch incomplete) — it does not re-dispatch the post-barrier aggregate.
3. **No completed-run re-replay consumer exists (Q2: NO).** `EngineOutputStore` is read EXCLUSIVELY by `_rehydrate_inter_step_channel_on_replay` (`:711`, reads at `:743`/`:749`), which is driven by `resume_at` (forward-from-crash) and gated `SINGLE_THREADED_LINEAR`-only (`:215-218`, `:818`, `:1814`, `:2001`). There is no path that re-executes a finished run from its event history.
4. **Read-surface enumeration (Q3):** every production read of an `EngineOutputStore` is the linear crash-resume rehydration above. Non-linear / terminal / driver-level outputs are read by **nothing**.

⇒ A captured terminal synthesis output would be **written and never read**. The only consumer that *could* exist is completed-run re-replay (does not exist; a large novel capability) or a fan-out **terminal-synthesis crash-resume reader** (lifting non-linear resume-blindness for the terminal aggregate — explicitly registered out-of-scope in the council design). Per the #705 lesson, a producer must ship with its non-vacuous consumer; OPTION-B-capture-only does not.

**Secondary (Q4, non-blocking):** the per-step step-ledger-entry + `response_hash` + audit machinery is welded to the inline §25.3 loop (`step_index`-scoped; IS computes `response_hash` at write-time). A post-barrier `POST_JOIN_SYNTHESIS` needs NEW post-barrier entry/append/disclosure machinery regardless of A-vs-B — this is legitimate, bounded arc-a impl work, not a blocker.

## Why this is a genuine operator gate (not a silent revert)

The operator explicitly chose B over A. Grounding now shows B's premise ("capture closes the window") is empirically false — the capture closes nothing (the window stays empty; the capture just sits unread). Honoring B genuinely requires ALSO building a large novel replay-consumer; B-capture-only re-creates #705. Reverting B→A without operator consent would silently override an explicit AUQ decision (root `CLAUDE.md` §10.8). High blast radius (committed-invariant amendment) ⇒ surface per `[[feedback-gate-only-on-meaningful-architecture-change]]`.

## The decision surfaced

- **A (recommended) — build the genuine non-hollow slice now; sequence the full reproducibility arc.** Arc-a builds: the opt-in `StepKind.POST_JOIN_SYNTHESIS` terminal step + re-opened §14.21 sibling-output recording (the synthesis is its **non-hollow consumer**) + the §25.12-Point-2 (aggregator-purity) amendment + loud disclosure (self-disclosing step entry + trace event) + default-byte-identical negative control. Register the full cached-replay **reproducibility** (capture **+** its replay/resume consumer, shipped together per #705) as a sequenced FULL-SPEC build arc `B-POSTJOIN-REPLAY-REPRODUCIBILITY`. Under FULL-SPEC this WILL be built — as a coherent producer+consumer arc, not a hollow producer now. The currently-wired harness has no divergence window, so nothing is sacrificed in the interim beyond the loud-disclosed forward-looking caveat.
- **B-full — honor "build cached-replay now" by building the capture AND its consumer.** Also build the large novel replay capability (completed-run re-replay, or a fan-out terminal-synthesis crash-resume reader under replay-capable engine classes) so the capture is genuinely read. Much larger scope; pulls a substantial new replay surface into arc-a to close a window that is currently empty.
- **(Not offered: B-hollow — build the capture now, consumer "deferred." This is the #705 anti-pattern itself and is not a co-equal option.)**

**Recommendation: A.** It is the council's original recommended shape, it enforces the committed #705 anti-hollow discipline, it is fully FULL-SPEC-consistent (the reproducibility becomes a registered build arc, not a defer), and it ships only genuine, full-chain-witnessable capability.

## RESOLUTION (operator AUQ 2026-06-22→23)

**Operator chose B-full** — *"also build the replay consumer now."* The FULL-SPEC posture applied (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`): build the genuine reproducible capability in arc-a, not the hollow capture (B-hollow, foreclosed) and not the sequenced follow-on (A). This HONORS the #705 discipline — the §14.23 capture (producer) ships WITH its non-vacuous replay consumer in the same arc; it does not re-create the hollow carrier.

**Arc-a scope is therefore the larger B-full set:**
1. CP spec: C-CP-25 §25.12 Point-2 (aggregator-purity sacrifice, opt-in) + StepKind §5.2/§25.2 6→7 (`POST_JOIN_SYNTHESIS`).
2. Runtime spec: §14.21 sibling-output recording re-open + §14.23 driver-level synthesis-output capture + **the NEW reproducible-replay consumer** (a fan-out terminal-synthesis replay reader under `EVENT_SOURCED_REPLAY`/`WAL_SEGMENT` — the genuine consumer that makes the capture non-hollow).
3. Impl (harness-cp): StepKind + the post-barrier `POST_JOIN_SYNTHESIS` dispatch + the new post-barrier step-entry/`response_hash`/audit machinery (Q4 — welded-to-inline-loop, so net-new but bounded).
4. Impl (harness-runtime): the dispatcher + EngineOutputStore (or sibling store) extension to capture the driver-level synthesis + **the replay consumer** that reads the captured synthesis on replay instead of re-dispatching.
5. Full-chain witnesses — incl. a witness that the captured synthesis is genuinely READ on replay (the non-hollow proof), through the REAL provider; default-byte-identical negative control; effect-free read-only-compose assertion; loud-disclosure audit.
6. Decorrelated review: adversarial reviewer + out-of-family Codex + advisor, reconcile-to-zero.

**The genuinely-new design surface** (the council left it out-of-scope and probe-resolved the tension by "the window is empty"): the reproducible-replay CONSUMER. It must be designed grounded against the actual `EVENT_SOURCED_REPLAY` substrate before spec text is written (`[[cleared-spec-resolves-it-before-first-principles-fix]]`). This is a reliability-mechanism design (advisor + code-grounding), NOT a fresh cross-domain council tension (the C1⊥C9 synthesis shape already converged).

## Coherent-design grounding (advisor-vetted 2026-06-22→23 — reachability ≠ consistency)

A first design pass proposed a BOUNDED synthesis-only cache-check at the fan-out `_finish` (read the captured synthesis on a resume that re-reaches `_finish`). **The advisor refuted this as #705-one-level-up:** reachability (does resume re-reach `_finish`) is necessary but NOT sufficient — the discriminator is CONSISTENCY: *is the captured synthesis ever read on a path where the branch inputs to it are identical to capture-time?* It is not. Empirically confirmed at HEAD `2dcd488`:

- **Branch outputs are UNCAPTURED.** `_record_durable_step_output` (→ `EngineOutputStore.record`) is called at exactly ONE site (`workflow_driver.py:2723`, the linear per-step loop). Fan-out branches persist via the buffered `append_branch_step_ledger_entry`/`append_branch_terminal_ledger_entry` path (a `response_hash` digest, never the output) → the store holds NO branch outputs.
- **Crash-resume RE-DIVERGES branches.** Non-linear strategies are resume-blind for every in-scope engine class (e-impl-1 §2 sub-finding) → a crashed fan-out restarts fresh → branches re-execute (LLM calls → different outputs). The B-FANOUT-PAUSE family (`arc-ledger.yaml:341/504/520/532`) is all PAUSE-resume (explicit snapshot), NOT crash-resume; there is NO registered fan-out crash-resume output-replay arc.

⇒ A synthesis-only cache-check would replay a synthesis on top of FRESHLY re-diverged branches = inconsistent garbage = a non-consuming consumer = #705 again. The bounded read is foreclosed.

### The coherent consumer (the advisor's "smallest coherent B-full")

For a replayed synthesis to be CONSISTENT, the branches under it must be reproduced too. The coherent B-full: **on crash-resume of a fan-out under `EVENT_SOURCED_REPLAY`/`WAL_SEGMENT`, replay ALL branch outputs from the store (skip branch re-execution) AND the synthesis output** — fail-closed on store↔ledger skew + identity mismatch, mirroring the linear `_rehydrate_inter_step_channel_on_replay` + the B-FANOUT-PAUSE identity gates. Clean framing: **extend the B-ENGINE-OUTPUT-REPLAY output-replay story from LINEAR to FAN-OUT** (branches become output-replayable on crash-resume), and the synthesis is just ONE MORE captured output riding the same machinery. This is exactly the "large novel replay surface" the operator was shown and chose (B-full over A) → BUILD it, do NOT re-ask (oscillation). Reuses patterns already read (RESERVE-before-COMMIT, fail-closed-skew, the journal store); substantial but well-defined, not novel-from-scratch.

### Decomposition (reversible — `[[r-cxa-seam-wiring-is-producer-discovery]]`)

The coherent build factors into two non-hollow capabilities; ledger checked — NO existing arc covers fan-out crash-resume output replay (the B-FANOUT-PAUSE family is pause-resume only):

1. **`B-FANOUT-OUTPUT-REPLAY` (NEW prerequisite)** — fan-out crash-resume output replay for the BRANCHES: capture branch outputs to the store + replay them on `EVENT_SOURCED_REPLAY`/`WAL_SEGMENT` crash-resume (skip branch re-execution), fail-closed on skew. The linear→fan-out analog of `B-ENGINE-OUTPUT-REPLAY`. **Independently non-hollow:** its consumer is the EXISTING deterministic aggregate fold, which becomes reproducible-across-crash-resume (a re-executed fan-out re-diverges; a replayed one does not).
2. **`B-POSTJOIN-LLM-SYNTHESIS` (arc-a, RIDES #1)** — the opt-in `POST_JOIN_SYNTHESIS` terminal step + §25.12-Point-2 amendment + §14.21 sibling recording + the synthesis-output capture (one more output on #1's machinery) + the synthesis replay (non-hollow BECAUSE the branches are now reproduced by #1).

Each ships its producer+consumer together (#705). 1-arc-vs-2-arc is reversible; decide at build-open. **Effect-safety note (advisor):** output-replay SKIPS branch re-execution → effects do not re-fire → at-most-once is PRESERVED (safer than re-execute); the synthesis is effect-free. No NEW committed-invariant sacrifice surfaced; if branch effect-replay semantics force one at build, that is a nameable C9 consult, surfaced then — not now.

### Process note
Per advisor: **note the coherent shape + size at PR time, NOT a fresh AUQ** (the operator already chose "large" over A — re-asking is oscillation). Escalate to a real gate ONLY if the build surfaces a new committed-invariant sacrifice.
