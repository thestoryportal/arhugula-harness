---
artifact: design-substrate/Spec_Control_Plane_v1_74.md
version: v1.74
cleared_at: 2026-06-26T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Control_Plane_v1_73.md §2 (registered B-FANOUT-EFFECT-FENCE-SCOPED-ABORT-CRASH-DURABLE, owner_axis "CP + runtime" — "persist the scoped-abort distinguishably in the durable record + reconstruct _scoped_abort_ordinals from recovered terminals; the disposition-vocabulary decision [replay-store vs IS-ledger] decided at open")
  - design-substrate/Spec_Control_Plane_v1_74.md §1 (the crash-durable scoped-abort persistence + reconstruct) + §2 (WHOLE close, registers nothing)
  - harness-cp/src/harness_cp/workflow_driver.py (the two _capture_branch_terminal scoped-abort sites now record terminal_status="scoped_aborted" to the store; the two recovered-terminal seed loops reconstruct _scoped_abort_ordinals from recovered "scoped_aborted" branches; the two _scoped_abort_to_record loops exclude already-recovered ordinals)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.84 §14.23 (the paired runtime delta — the EngineOutputStore disposition vocabulary grows {completed, timed_out} → {completed, timed_out, scoped_aborted})
  - .harness/clearance/Spec_Harness_Runtime-v1_84-cleared-2026-06-26.md (the paired runtime marker)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor (full-transcript) — BEFORE substantive work: confirmed the arc pick (most contained, freshest, non-gated of the 4 forward) + the A-vs-B replay-store-vs-IS-ledger determination (the store terminal_status is a free str disjoint from the IS Literal → option B is sound + CP-only-IS, no §5.2 IS-hash arc); flagged the ENFORCED read-back guard (must extend additively or a mixed abort+survivor recovery fails closed), the both-sites symmetry, and the result-fidelity (not no-double-fire) witness bar.
  - out-of-family Codex — diff review owed pre-merge.
  - by-execution witnesses: genuine producer→crash→consumer chains (a real effect-fence pause → ABORT_BRANCH resume WRITES the store, then a fresh-ledger run RECONSTRUCTS from it) at BOTH topologies (PARALLELIZATION all-abort → FAILED + mixed → PARTIAL; ORCHESTRATOR_WORKERS all-abort → FAILED) — each RED-without-fix verified (without the seed-loop reconstruct the all-abort crash-resume returns PARTIAL with empty aggregate); + the runtime store round-trip witness (test_engine_output_store.py). harness-cp 217 fan-out/pause tests + 37 runtime store tests pass; pyright 0/0/0; ruff clean.
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.74`

v1.74 is a **change-note-level bundled-absorption** delta (co-published with `harness-cp` + `harness-runtime` impl + tests + the paired runtime delta v1.84) — the CP half of the registered R-FS-1 arc `B-FANOUT-EFFECT-FENCE-SCOPED-ABORT-CRASH-DURABLE`, a **WHOLE close**.

- **The crash-durable persistence (the v1.73 §2 residual).** v1.73 §1 delivered the IN-RESUME per-branch-SCOPED abort (`ABORT_BRANCH`) but reused the `completed`/no-output terminal in the durable crash-resume store, so a scoped-abort branch was INDISTINGUISHABLE from a ran-and-errored one on crash-resume — an ALL-scoped-abort resume that CRASHED after the captures reconstructed PAUSED→PARTIAL, not the in-resume all-abort FAILED (status-fidelity only; NO double-fire — a recovered terminal is never re-dispatched).
- **The fix (replay-store side, not IS ledger).** The store records a scoped-abort branch under the DISTINCT disposition `scoped_aborted`; the CP crash-resume reconstruct reads it back into `_scoped_abort_ordinals` from the recovered terminals at BOTH fan-out sites, so the existing all-abort guard reproduces FAILED (all-abort) / PARTIAL (mixed) across a crash. The IS-hash-bearing F2 ledger terminal entry STAYS `completed` (no §5.2 IS-hash change, no cross-axis cascade); only the runtime crash-resume store carries the distinguishing value.

## Caveats for Phase 7 consumers

- Change-note-level: ADDITIVE. No contract removal, no committed-invariant sacrifice; at-most-once PRESERVED (the scoped-abort branch is a recovered terminal on crash-resume, never re-dispatched; recovered ordinals are excluded from the re-record loop so no duplicate ledger terminal). No new C-CP contract; no closed-enum change (the additive store disposition is a runtime free-str value, NOT the IS `terminal_status` Literal); no new CXA edge. The v1.73 §1 in-resume scoped-abort body + the C-CP-01..C-CP-29 body PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- **Runtime spec §14.23 C-RT-32 v1.83 → v1.84** is the paired delta (the store disposition vocabulary extension).
- **WHOLE close** — registers nothing; `closure_gate.py` G1.1 `standalone_registered` 4 → 3.
