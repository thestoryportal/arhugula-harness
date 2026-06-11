# Class 2 Fork — engine-layer durable-resume (Gate A) has no production producer; the real gap is workflow-layer

**Status:** OPEN — awaiting operator scoping decision (Class 2, in-execution operator decision per `Project_Workflow_v1_8.md` §2.7.6 / root `CLAUDE.md` §4.3).
**Filed:** 2026-06-12 · **Posture:** mode-agnostic (back-flow documentation; no `harness-*/src` or `design-substrate/**` edit — those wait on the decision).
**Arc:** R-CC-1 capability-completion program, **arc #3** (`.harness/capability-completion-inventory-v1.md` item #6).
**Authority in tension:** operator **Gate A** (2026-06-11, hand-roll) ⊥ operator-ratified **forward-register line 181** (`.harness/post-phase-8-forward-register.md`, CXA-2 close-out).
**Prior art:** `.harness/class_2_fork_r_cxa_2_producer_loop_ownership.md`; `.harness/r-cl-p2-engine-recovery-grounding.md` (the original DEFER that Gate A overrode).
**Grounded at HEAD `f369e21` by direct read this session** (cites resolved, not recalled).

---

## 1. What Gate A authorized, and the assumption it rested on

> Capability inventory §3, Gate A (2026-06-11): *"Build a real in-house event-sourced/journal recovery substrate (preserving I-6 — no vendored engine), with a real production caller. … the genuine engine-layer semantic is **durable-resume / crash-recovery** (resume a workflow from the #475 journal after a process restart), with `api.run` resume-from-journal as the real caller."*

The inventory itself flagged the load-bearing risk (item #6 row): **"risk: caller must be real"** and **"the missing piece is the real durable-resume semantic + caller."** Gate A overrode the 2026-06-10 P2 DEFER recommendation on the premise that a *real caller* could be supplied. This fork records that **grounding at HEAD falsifies that premise on the engine-layer**, and that the only honest build re-aims to a different layer than Gate A named.

## 2. Grounded state of the world (the producer is the discriminator)

There are **two distinct pause/resume layers** in the same `harness_cp.pause_resume_protocol` module:

| Layer | Type | Production producer at HEAD? | Durable store? | Resumable across process restart? |
|---|---|---|---|---|
| **Engine-layer** `ctx.engine_recovery_loop` | `EnginePauseResumeSubstrate` | **NO** — `capture_pause`/`attempt_resume` called only by `test_r_cxa_2_producer_loop_factory.py` | journal substrate #475 exists but **unbound** (factory binds in-memory `Deterministic`, `r_cxa_2_producer_loop_factory.py:210`) | n/a (no producer) |
| **Workflow-layer** `ctx.pause_resume_protocol` | `PauseResumeProtocol` | **YES** — DURABLE_ASYNC HITL pause fires `capture_pause_snapshot` at `workflow_driver.py:796` + `:952` | IS state ledger (durable) **+ MVP placeholder `pause_context_reader`** (empty `StateSummary`, sentinel anchor — `pause_resume_protocol_factory.py:85-100`) | **NO** — resume (`attempt_resume`) reachable only in-process at `workflow_driver.py:571`; **`api.run` has no resume input** (`api.py:389` — `run(workflow, *, config)`, bootstrap-per-call under `_run_lock`; a restart = fresh full re-execution) |

**Discriminator (the producer, not the resume reader).** `api.run` resume-from-journal reading a journal that nothing writes in production is still a fake producer, just relocated to the read side. The decisive fact is that the engine-layer loop has **no production pause producer** and cannot get one honestly:

- The engines that emit engine-layer pauses (Temporal / K8s / Kafka / LangGraph) are **I-6-forbidden to vendor**.
- The only candidate producer is the workflow-layer DURABLE_ASYNC pause — and piping that through the engine loop is **exactly** what line 181 forbids.

> Forward-register line 181 (byte-exact, CXA-2 close-out): *"Do not wire `workflow_driver.py` as a fake engine recovery loop; re-open only when a real event-sourced replay, reconciler-loop, WAL-segment, or engine-native-pause recovery loop lands."*

So binding #475 into the engine_recovery_loop factory (the literal Gate A action) is the **cosmetic swap** the P2 doc named: invisible in every production path, and it forces resolving the journal `PathClass` against the **closed 4-class enum** (`path_class_registry.py`; IS-AL-1 forecloses inventing one) for **zero production benefit**.

## 3. The real gap is workflow-layer, which diverges from Gate A's engine-layer framing

The genuinely real, line-181-respecting, buildable gap is on the **workflow-layer**:
1. **No `api.run` resume entry-point** → a DURABLE_ASYNC HITL pause cannot be resumed after a process restart via the public API at all.
2. **MVP placeholder pause content** → even in-process, the captured `StateSummary` is empty (`pause_resume_protocol_factory.py:_make_default_pause_context_reader`), so there is no genuinely-resumable state.

Building this satisfies the *spirit* of Gate A (a real hand-rolled durable-resume / crash-recovery with a real caller) while respecting line 181 (the engine-layer loop stays the ratified CXA-2 bounded-residual awaiting a real external-engine driver). **But it re-aims arc #3 from the engine-layer (item #6) to the workflow-layer — a material divergence from what Gate A named, and it adds net-new public API on the cleared C-RT-08 `api.run` contract → design-fork-first (X-AL-3): a runtime-spec amendment before impl.** That re-aim is the operator's call, not a silent Phase-7 re-direction.

**Nameable cross-domain tension** (why this is a genuine fork, not a mechanical pick): C9 reliability/crash-recovery (*wants* real durable-resume) ⊥ C10 blast-radius + I-6 no-vendor-framework discipline (*wants* no fake producer, no vendored engine, minimal new surface), across the engine-layer-vs-workflow-layer architectural boundary (C1).

## 4. Options

| # | Option | What it builds | Honesty / cost |
|---|---|---|---|
| **1 (RECOMMENDED)** | **Re-aim arc #3 to the workflow-layer durable-resume gap** | A real `api.run` resume entry-point (resume a paused workflow after a restart) + upgrade the workflow-layer DURABLE_ASYNC pause to capture genuinely-resumable content, backed by a durable store (repurpose #475's journal as the workflow-layer durable store, or the IS ledger). | Honest, real, line-181-respecting; satisfies Gate A's *spirit*. **Larger arc**: design-fork-first (net-new public API on cleared C-RT-08 `api.run` → runtime-spec amendment + clearance before impl). |
| 2 | **Literal Gate A — bind #475 into the engine_recovery_loop factory** | Swap `Deterministic`→`Journal` in `r_cxa_2_producer_loop_factory.py`. | **Cosmetic / fake-producer anti-pattern** (no production producer; forces closed-`PathClass` extension for zero benefit). The exact thing P2 + line 181 forbid. **Not recommended.** |
| 3 | **Confirm DEFER — keep engine-layer durable-resume as the ratified CXA-2 bounded-residual; advance to arc #4** | No build. Re-open trigger stays = a real external-engine driver lands (I-6-gated). | Honors line 181 as-is = reverses the Gate A override given the new grounding. Advances R-CC-1 to arc #4 (api.run provider-ping fork) + P3 live multi-tier e2e (free Ollama). |

## 5. Recommendation

**Option 1** if the operator wants real durable-resume capability landed now (accepting the larger design-fork-first arc on the workflow-layer + a net-new `api.run` resume surface). **Option 3** if the operator prefers to keep the R-CC-1 program moving and treat durable-resume as the already-ratified bounded-residual (re-open when a real external-engine recovery driver is in scope). **Not Option 2** under any reading — it is the fake-producer swap the workspace has twice ruled out.

## 6. Disposition

- **RESOLVED → Option 1 (re-aim to workflow-layer).** Operator chose "Re-aim to workflow-layer (Rec.)" via AskUserQuestion 2026-06-12.
- **Next:** open the design-fork — author a design doc under `.harness/` for the workflow-layer durable-resume semantic + the `api.run` resume surface (R-PM-1 arc-#2 precedent: `.harness/` design doc first → per-axis spec cascade → impl). The net-new public API on the cleared C-RT-08 `api.run` contract is the X-AL-3 reason design precedes impl. The engine-layer `engine_recovery_loop` stays the ratified CXA-2 bounded-residual (line 181 unviolated — it is NOT the build target).
- Design doc: `.harness/r-cc-1-arc-3-workflow-durable-resume-design-v1.md` (this arc).
