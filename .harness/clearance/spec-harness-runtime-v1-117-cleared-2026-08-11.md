---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.117
cleared_at: 2026-08-11T21:15:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b150_collector_stop_ordering_deferral.md
  - .harness/forward-register.yaml B-150 row (grounded_2026_08_11 block)
  - "PR #1305 (falsifier grounding) + PR #1307 (atexit half, impl-only)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "loop-mode /resolve: transcript advisor VOTE A (3 corrections absorbed: vacuous-at-HEAD reground; :3757 second invariant; loop-bound stop constraint); codex vote UNPARSEABLE across 3 attempts (agentic despite answer-only; its own worktree impl was A-shaped) — recorded, not counted"
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - merge-gate 3-lens (code-touching PR)
supersedes: spec-harness-runtime-v1-116-cleared-2026-08-11.md
---

# Clearance — Spec_Harness_Runtime v1.117 (B-150 collector-half deferral)

**What v1.117 changes.** Four sites, all inside §10 C-RT-10:

1. The step-3 collector bullet gains the in-flight-conditional deferral its 3b
   sibling machinery already carries: a timed-out flush worker still exporting
   skips the inline stop, reports `collector_daemon`, and the stop executes on
   the deferred chain; a worker finishing between 3a and 3b completes the stop
   INLINE at 3b time with the tag withdrawn. 3a→3b order holds on EVERY path.
2. A NEW deferred-close-discipline paragraph ratifies the as-built B-147/#1307
   machinery in contract text (one watcher, 3a→3b order, ordered atexit
   backstop, loop-bound stop scheduled thread-safely with closed-loop ⇒
   terminated, deferred closes excluded from the `timeout` bound, and the
   honest NARROWS-not-eliminates scope of the deferral).
3. Step-6 "Collector daemon process/thread terminated" → terminated OR
   owned-by-the-deferred-chain.
4. Step-6 "No background task remaining on the asyncio event loop" → qualified
   for the deferred path only (the daemon's `_run_loop` task may remain until
   the deferred stop lands or dies with the loop/process).

**Forward-correctness framing (advisor catch).** The collector daemon at
v1.117 is a receiver-less supervisor scaffold, so the late-export window is
presently VACUOUS; the rejected carve-out would have permanently ratified span
loss against C-RT-10's own PRD enablement for exactly the future in which the
live receiver makes both the loss and the deferral's repair real.

**Not a design extension (X-AL-3).** No new contract numbers; no CXA rows; no
OD/CP/IS/AS delta; no hash impact; normal-path behavior byte-identical. Paired
impl in the SAME PR (bundled absorption per §11.4): the step-3a mirror
condition, the between-3a-and-3b inline completion, the watcher-chain
collector stop with loop-dead guard; three witnesses (deferred-order timeline;
frame-scoped race-path branch witness; loop-dead guard), two mutation probes
run RED (the second probe caught and fixed a vacuous first draft of the
race-path witness), and the full #1303 witness set re-run green (84/84) per
the register close_out step 3.

**Register effect.** B-150 CLOSES at this leg (atexit half #1307; collector
half here). B-151 (backstop residuals) unaffected.
