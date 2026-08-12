---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.118
cleared_at: 2026-08-11T19:45:00-07:00
clearance_type: spec-writer-apply-pass
back_reference:
  - ".harness/forward-register.yaml B-152 row (registered at PR #1310; codex round-2 findings, lens-1 adjudication)"
  - "PR #1310 (registration + the lens-2 C-RT-07 recorded residual this leg discharges)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - "merge-gate spec-conformance lens (lean protocol — doc-only spec delta, #1308 precedent)"
supersedes: spec-harness-runtime-v1-117-cleared-2026-08-11.md
---

# Clearance — Spec_Harness_Runtime v1.118 (B-152 deferral-unavailable boundary declarations)

**What v1.118 changes.** FOUR qualification clauses at TWO contracts (§7
C-RT-07 + §10 C-RT-10), no new machinery. The two lead clauses below, plus two
stale-carry companions absorbed at out-of-family round 1 (the carve-out would
otherwise contradict two remaining absolute promises): the §10 deferred-close
paragraph's "executed by ONE watcher" now reads when-the-watcher-LAUNCHES, and
C-RT-07's "no collector persists across runs" carries BOTH embedder-only
boundaries — launch failure AND the stopped-but-open-loop skip on a later-
resumed loop (round-2 catch; embedder-only; unreachable in-repo):

1. C-RT-07 §7 lifecycle invariant *"No collector survives harness shutdown"*
   qualified deferred-path-only: the stop may land after the `shutdown()` CALL
   returns (never after the loop/process) — the qualification the v1.117 leg
   owed (the #1310 lens-2 recorded residual). The stalled-loop late-stop
   residual (codex P1) is subsumed as vacuous in-repo: every entry point
   hosting `shutdown()` runs on an `asyncio.run`-managed loop (closed on
   return), grounded at `cli/app.py:299/:342/:615`, HEAD `25f2e5a3`; the CP
   fan-out loop is private and never hosts `shutdown()`.
2. §10 step-6 collector invariant gains the watcher-launch-failure carve-out
   (codex P2): `Thread.start` failure leaves NO deferred chain — the collector
   remains live until the loop/process dies, both skipped closes stay
   reported; the on-loop fallback is REJECTED with grounds (second
   close-ownership mechanism; unbounded worker wait — the class B-147
   removed; the fallback itself can fail to schedule).

**Not a design extension (X-AL-3).** No new contract numbers; no CXA rows; no
OD/CP/IS/AS delta; no hash impact; ZERO code change — both qualifications
describe as-built `shutdown.py` behavior (the `Thread.start` catch-and-continue
and the loop-bound stop guard are unchanged); no plan units owed.

**Register effect.** B-152 CLOSES at this leg. Falsifiers preserved: a Runtime
delta retiring the deferred chain, or the live OTLP receiver arc restructuring
collector ownership, re-opens both questions there.
