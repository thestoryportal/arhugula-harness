---
artifact: design-substrate/Spec_Control_Plane_v1_91.md
version: v1.91
cleared_at: 2026-07-11T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/u1-3c-prewarm-design-decision-record.md §11.5 M2 ("decide + test the disposition of never-released siblings")
  - B-18-3C-PREWARM-TIMEOUT-LEDGER (arc-ledger)
merge_commit: pending (marker rides the bundled-absorption PR)
reviewer_chain:
  - Fable-5 adversarial pre-build DESIGN review (this session; advisor tool unavailable + Codex TLS-blocked in bg jobs — standing fallback ladder per [[fable5-fallback-reviewer]]) — VERDICT AMEND, 0 blocking / 5 concern / 3 cosmetic; every cited anchor independently re-grounded at HEAD; C1 (v1.44 §1 re-scope) / C2 (protocol-not-bound exit included) / C3 (dedup residual named + ML7 key-collision witness) / C4 (single shared helper + PROCEED handler merge) / C5 (fence-arm live-on-strict-tiers/unreachable-on-PROCEED documented) all incorporated before build
  - Reviewer confirmations (refutation attempts that failed) — `cancelled` is the only obligation-4-legal disposition; a store write would poison crash-resume (store terminal outside {completed,timed_out,scoped_aborted} = corrupt; synthesized `timed_out` would trip the fail-closed ambiguity gate); no consumer keys `cancelled` to the CASCADE_CANCEL tier; crash-resume entry gates read store/markers only
  - impl witnesses (7 new ML1–ML7 tests; harness-cp full suite 1502 green; workspace pyright 0/0/0; ruff clean; runtime non-e2e + IS/AS/OD green recorded at the PR)
  - post-build decorrelated diff review recorded at the PR
---

# Clearance — `Spec_Control_Plane_v1_91.md`

This delta closes **B-18-3C-PREWARM-TIMEOUT-LEDGER** (DDR §11.5 M2): when the §25.11 deadline fires during warm-up Phase 1, branches[1..N-1] were never dispatched and previously left ZERO ledger footprint on the PROCEED (→ PARTIAL) and PAUSE deadline-strike (→ FAILED) exits — indistinguishable, to an auditor, from lost entries. The fix synthesizes the §25.15.2 **obligation-4 `cancelled` terminal** (terminal-ONLY, LEDGER-only) for every branch with no step/terminal disposition, at every TERMINAL fan-out exit: CASCADE_CANCEL post-barrier (pre-existing scan, now the shared helper), PROCEED deadline → PARTIAL, PAUSE deadline → FAILED, and PAUSE protocol-not-bound → FAILED (review amendment C2). The branch-failure → PAUSED boundary stays scan-free — snapshot OMISSION is the re-dispatchable contract (v1.44 §1, re-scoped to exactly that boundary at v1.91 item 4).

**The disposition decision is the load-bearing clearance fact.** The arc row anticipated "synthesize `timed_out` entries"; the DDR left the disposition explicitly open. `timed_out` is the ambiguous in-flight class (effect may have landed; crash-resume fails closed) — synthesizing it for provably-never-dispatched branches would conflate the obligation-4 discriminator's two classes. `cancelled` is the pinned not-yet-dispatched vocabulary. The pre-build review confirmed no spec text anywhere commits `timed_out` for never-released branches, and that the store must NOT be written (marker-absence = the durable provably-never-ran witness, v1.90 §25.17 item 4 — preserved byte-exact).

**The C3 residual is named, bounded, and witnessed.** Synthesized ledger terminals are per-attempt audit records, not resume authority. On a stale-snapshot double-resume, the re-run's real terminal composes the identical deterministic idempotency key and IDEMPOTENT-NOOPs at the shared real ledger, leaving the first attempt's `cancelled` standing (result/store fidelity unaffected). ML7 pins the key collision.

## Notes

- NO §5.2 IS-hash change (ledger terminal Literal already carries `cancelled`); NO new contract/enum/fail-class/CXA edge; runtime spec UNCHANGED.
- Baseline byte-preserved: the scan keys on disposition ABSENCE — every started branch carries its own disposition, so non-warm-up deadline strikes synthesize nothing (ML6).
- `B-18-EPOCH-PARTITION` remains the sole open B-18 follow-on (dedicated session).
