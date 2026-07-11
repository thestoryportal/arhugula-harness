---
artifact: design-substrate/Spec_Control_Plane_v1_90.md
version: v1.90
cleared_at: 2026-07-11T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/b18-3c-prewarm-cascade-ddr.md (Fable-5 review-cleared pre-build DDR; §3b Option A operator-ratified 2026-07-11, probe-resolved in §10 addendum)
  - B-18-3C-PREWARM-CASCADE (arc-ledger)
merge_commit: pending (pre-push; bg-session push-blocked — see close report)
reviewer_chain:
  - Fable-5 adversarial pre-build DDR review (2026-07-11) — R1-R5/C1-C4/M1 incorporated at the DDR before build
  - Empirical §3b probe on HEAD (2026-07-11, pre-build) — refuted the R2 crash-window gap; Option A vacuous
  - Fable-5 adversarial diff review (this session; Codex TLS-blocked in bg jobs — standing fallback ladder) — VERDICT 0 blocking / 3 concern / 5 cosmetic; D4 independently re-ran the probe + confirmed the §3b vacuity (and sharpened it: unguarded-as-sketched Option A would regress the W3 resume leg); all concerns resolved in-arc (spec+clearance bundled, DDR §10 addendum, W7 added)
  - impl witnesses (10 new B-18-3C-PREWARM-CASCADE tests incl. W7 R3-guard pair; harness-cp full suite green, runtime non-e2e 2360 green, other axes 1590 green, workspace pyright 0/0/0)
---

# Clearance — `Spec_Control_Plane_v1_90.md`

This delta extends **ADR-D4 §1.8** concurrent-prompt-cache warm-up from the PROCEED path (v1.87) to the strict tiers (CASCADE_CANCEL + PAUSE) at `_cancel_fanout`. `_same_prefix_cohort()` + `_warmup_gate` lift above the cascade_policy branch (one gate, three paths); the strict-tier fan-out gains a two-phase form — branch[0] solo (cache-write), then branches[1..N-1] under TaskGroup (cache-hits) — sharing ONE `asyncio.timeout(deadline)` + ONE `_BRANCH_INFLIGHT_DISPATCHES` watchdog (never two barrier calls, which would double the §25.11 budget). Phase 1 carries the Fable-5 R3-corrected guard (`except asyncio.CancelledError: raise` only; other exceptions wrap into `BaseExceptionGroup("cascade-warmup-branch0", …)` so the post-barrier classification is byte-consistent with the TaskGroup path).

**The §3b disposition is the load-bearing clearance fact.** The DDR's Fable-5 R2 finding claimed a crash window (branch[0] recovered `completed`/no-output, siblings never dispatched, PAUSED snapshot lost) silently produced PARTIAL, and the operator ratified Option A (pre-barrier `branch_failed` synthesis) to close it. A pre-build empirical probe on HEAD refuted the premise: the entry-time crash-resume gate (v1.68/v1.70/v1.71 reconstruct machinery) already re-establishes PAUSED (PAUSE tier; zero re-dispatches) / reproduces FAILED (CASCADE_CANCEL tier) for exactly that state — the DDR's "branch_plan non-empty → barrier runs" premise was stale against `_crash_pause_reconstruct_no_dispatch`. Option A was therefore NOT built (it would be dead code asserting a gap that does not exist); the operator's ratified intent — never a silent PARTIAL in the crash window — is pinned permanently by witness W6, which produces the crash state organically through the new warm-up path and asserts the re-entry re-pauses with zero dispatches.

Effect-set: a Phase-1 failure WITHHOLDS the siblings entirely (no reserve-before-dispatch marker) — a strict subset of the non-warmup effect-set; W2 witnesses marker ABSENCE per Fable-5 M1. Records equivalence: the same `_cancel_branch` writes the same markers + terminals under either routing, so all recovery paths consume byte-equivalent state.

## Notes

- NO §5.2 IS-hash change, NO new contract/enum/fail-class/CXA edge; runtime spec UNCHANGED.
- Gate=False (non-`CohortKeyCapable`, or manifest opt-out) routes to the pre-arc `cascade_cancel_barrier` verbatim (W4 baseline witness).
- `B-18-3C-PREWARM-TIMEOUT-LEDGER` (registered) now also covers the strict-tier Phase-1 deadline-audit gap.
