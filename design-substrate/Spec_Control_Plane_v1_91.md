# Spec: Control Plane — v1.91 (delta over v1.90)

*Delta-only file. The v1.90 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-3C-PREWARM-TIMEOUT-LEDGER bundled-absorption arc (DDR §11.5 "M2"): obligation-4 `cancelled` terminals synthesized at the four terminal PARALLELIZATION fan-out exits enumerated at item 2 for branches withheld past the boundary, closing the audit-visibility gap when the asyncio deadline fires during warm-up Phase 1 (registered at v1.87, extended to the strict tiers at v1.90). The fence-ABORT terminal exit is deliberately NOT in scope — see item 6.*

## Change-note (v1.90 → v1.91)

**What this materializes.** Under the ADR-D4 §1.8 warm-up (v1.87 PROCEED; v1.90 strict tiers), a deadline strike during Phase 1 (`branch[0]` serialized) means branches[1..N-1] were **never dispatched** — and, prior to this delta, left **zero ledger footprint** on the PROCEED (→ PARTIAL) and PAUSE deadline-strike (→ FAILED `parallelization-barrier-deadline`) exits, unlike the all-concurrent baseline where every in-flight branch records its step + `timed_out` terminal at its own CancelledError handler. A compliance reader of such a run's ledger could not distinguish "withheld" from "lost entries". CASCADE_CANCEL never had the gap on its cascade-policy exits (its obligation-4 scan runs before the deadline/branch-failure classification — though after the tier-agnostic fence-ABORT return, item 6). Design authority: `.harness/u1-3c-prewarm-design-decision-record.md` §11.5 M2 ("decide + test the disposition of never-released siblings") + the pre-build Fable-5 adversarial design review (this arc; VERDICT AMEND, 0 blocking, C1–C5 amendments all incorporated).

**Scope of revision — §25.17 addendum (M2 terminal-exit synthesis):**

1. **Disposition decided: `cancelled`, NOT `timed_out`.** The §25.15.2 obligation-4 discriminator is load-bearing: `cancelled` ⟹ not-yet-dispatched boundary (provably no effect); `timed_out` ⟹ the branch's in-flight step was deadline-cut (ambiguous — the effect may have landed; crash-resume fails closed on it). Synthesizing `timed_out` for provably-never-dispatched branches would conflate the two classes. *(The arc-ledger row's `anticipated_scope` wording "synthesize timed_out entries" was registration-time anticipation, not a ratified disposition — the DDR line explicitly left it open; the divergence is deliberate and review-confirmed.)*

2. **One shared scan at every TERMINAL exit.** The CASCADE_CANCEL obligation-4 scan is factored into `_synthesize_undispatched_terminals()` (one helper, closure-scoped in `_execute_parallelization`) and now runs at **four** terminal exits: (a) CASCADE_CANCEL post-barrier (pre-existing, unchanged semantics); (b) PROCEED deadline handlers → PARTIAL (the two handlers merged to one `except (BranchBarrierDeadlineExceededError, TimeoutError)` — the former is unreachable from `_proceed_fanout`, merged without semantic loss); (c) PAUSE `deadline_struck` → FAILED `parallelization-barrier-deadline`; (d) PAUSE protocol-not-bound → FAILED `parallelization-pause-resume-protocol-not-bound` (review amendment C2: under warm-up a Phase-1 branch[0] failure withholds ALL siblings, and with no snapshot the re-dispatchable-by-omission defense does not apply — zero footprint there would be systematically indistinguishable from lost entries). The scan is keyed on the ABSENCE of a step/terminal disposition (not warm-up state, not an empty buffer — an overridden branch carries its `branch_metadata=None` override entry), so the non-warm-up baseline — where every started branch already carries its own disposition — is byte-preserved, and the theoretical baseline never-started-at-cut window is honestly covered too.

3. **Terminal-ONLY, LEDGER-only.** A synthesized entry is a terminal entry only — a step entry would claim a dispatch that never fired. NO `_mark_branch_dispatched` and NO `_capture_branch_terminal` for a never-dispatched branch: dispatch-marker ABSENCE remains the durable provably-never-ran witness (v1.90 §25.17 item 4 — the effect-set invariant is untouched), and a store terminal outside {`completed`, `timed_out`, `scoped_aborted`} is corrupt to crash-resume. The effect-fence-paused arm is preserved inside the shared helper (a fence-paused peer DID dispatch → `completed` + the durable store capture, Codex [P2]); it is live on the strict tiers (a deadline can race a fence-pause) and structurally unreachable under PROCEED (`_proceed_branch` has no fence path; PROCEED fence-resumes are rejected fail-closed pre-dispatch) — documented, not discovered.

4. **v1.44 §1 re-scope (review amendment C1).** The v1.44 change-note sentence — "the not-yet-dispatched ones are LEFT re-dispatchable (NO `cancelled` terminal — the cascade-cancel obligation-4 scan is deliberately NOT run on the `pause` path)" — is hereby **scoped to the branch-failure → PAUSED boundary only** (the resumable boundary, where snapshot OMISSION is the re-dispatchable contract and remains scan-free — witnessed at ML5). The PAUSE tier's *terminal FAILED* exits (deadline-strike; protocol-not-bound) are NOT that boundary — nothing resumes them — and DO run the scan per item 2. The unscoped v1.44 sentence is superseded to exactly this extent; §25.15.1 pause semantics are otherwise unchanged.

5. **Obligation-7 reading + the C3 residual (recorded).** Synthesized ledger terminals are **PER-ATTEMPT AUDIT records, not resume authority**: re-dispatch eligibility keys on snapshot omission (v1.44 §1), never on a ledger terminal read — so a synthesized `cancelled` does NOT mark its branch terminal for §25.15.2 obligation-7 purposes. Residual (bounded, review-named C3): after a resume attempt that deadline-strikes in Phase 1 (FAILED + synthesized `cancelled` drained), a second resume from the same still-journaled snapshot re-dispatches the sibling, and its REAL terminal composes the IDENTICAL deterministic idempotency key (run-key × step_index × branch-terminal path) — at the shared real IS ledger that append IDEMPOTENT-NOOPs, so the first attempt's `cancelled` stands in the audit trail while the store/aggregate/result remain correct. Witnessed at ML7 as the key collision. Inherited-in-shape from the pre-existing CASCADE_CANCEL scan; newly reachable on a resumable-workflow path.

6. **Out-of-scope fence-state audit fidelity (post-build review; registered follow-on `B-18-FENCE-LEDGER-FIDELITY`).** Two fence-family findings from the post-build decorrelated diff review are deliberately NOT fixed in this delta — their correct dispositions carry open semantic questions (notably store-capture-or-not for a cross-attempt fence peer) that belong to their own design pass:
   (a) **Fence-ABORT terminal exit bypass** — the tier-agnostic `parallelization-effect-fence-aborted` FAILED return fires BEFORE every scan site (pre-existing exit shape, unchanged on main). Under warm-up, a Phase-1 `EffectFenceAbortedError` withholds all siblings and this exit records zero footprint for the aborted branch and the withheld siblings. Naively running the scan there would mislabel the ABORTED branch `cancelled` (it DID dispatch — the fence arm keys on the *paused* dict, not the *aborted* set), so inclusion requires its own disposition mapping.
   (b) **Snapshot-carried fence-peer asymmetry** — the scan's fence arm consults this-round `effect_fence_paused_dispositions` only, not the snapshot-carried `_recovered_effect_fence_paused`. A previously-fence-paused peer re-dispatched on a resume round and withheld by a Phase-1 deadline strike synthesizes `cancelled`, which is false cross-attempt (its prior dispatch fired; its store marker + fence state remain honest — audit-surface only).
   Both are bounded to compound fence × warm-up × deadline paths; store markers, snapshots, resume, and crash-resume stay honest throughout (review-confirmed). The prose scope of this delta is exactly the four exits at item 2.

**New witnesses** (`harness-cp/tests/test_workflow_driver_parallelization_warmup.py`, B-18-3C-PREWARM-TIMEOUT-LEDGER section):

| # | Test | Pins |
|---|---|---|
| ML1 | `test_proceed_warmup_phase1_deadline_strike_records_cancelled_for_withheld` | PROCEED Phase-1 strike → PARTIAL; siblings `cancelled` terminal-only; store gets no sibling record |
| ML2 | `test_pause_warmup_phase1_deadline_strike_failed_with_cancelled_terminals` | PAUSE deadline → FAILED `parallelization-barrier-deadline`; siblings `cancelled` in ledger + dispatch-marker ABSENCE in store |
| ML3 | `test_cascade_cancel_warmup_phase1_deadline_strike_cancelled_via_scan` | CASCADE_CANCEL deadline path preserved through the shared helper (regression) |
| ML4 | `test_pause_warmup_branch0_failure_protocol_not_bound_records_cancelled` | C2 exit runs the scan (no snapshot → omission ≠ re-dispatchable) |
| ML5 | `test_pause_warmup_branch0_failure_paused_siblings_zero_ledger_footprint` | Negative control: branch-failure → PAUSED stays scan-free (item 4 boundary) |
| ML6 | `test_baseline_all_concurrent_deadline_strike_no_cancelled_synthesis` | Gate=False all-concurrent strike: all `timed_out`, nothing synthesized (baseline byte-preserved) |
| ML7 | `test_stale_snapshot_double_resume_synthesized_cancelled_key_collides` | C3 residual: synthesized-`cancelled` / real-`completed` idempotency-key collision |

**Invariants preserved.** NO §5.2 IS-hash change (the ledger terminal Literal already carries `cancelled`; no new field, no new enum value). NO new contract / ADR / fail-class / CXA edge. Dispatch markers + store captures byte-unchanged for never-dispatched branches (marker-absence invariant). `workflow.step_count` unaffected (terminal-only entries carry no step entry; the drain counts step entries — the stale `_drain_and_emit_step_boundaries` docstring claim that PARALLELIZATION "never buffers a terminal-only branch" is corrected in the same arc). Gate=False + non-deadline paths byte-identical (ML6 + full-suite green).

Suite state at close: harness-cp full suite 1502 passed (7 new witnesses); workspace pyright 0 errors / 0 warnings / 0 informations; ruff clean; harness-runtime non-e2e + IS/AS/OD suites green (recorded at the PR).

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-3C-PREWARM-COHORTKEY` | Dispatcher-oracle `CohortKeyCapable` Protocol | CLOSED (v1.88) |
| `B-18-3C-PREWARM-DEFAULT-ON` | Flip to required-at-cap>1 per ADR §1.8(f) | CLOSED (v1.89) |
| `B-18-3C-PREWARM-CASCADE` | warm-up on CASCADE_CANCEL + PAUSE paths | CLOSED (v1.90) |
| `B-18-3C-PREWARM-TIMEOUT-LEDGER` | M2 terminal-exit audit completeness | **CLOSED (this arc)** |
| `B-18-FENCE-LEDGER-FIDELITY` | Fence-state × terminal-exit audit records: the fence-ABORT exit bypass + the snapshot-carried fence-peer arm (item 6a/6b) | **Registered (this arc, post-build review)** |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition | Registered, open (dedicated session) |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_91.md` (delta over v1.90) |
| Arc | B-18-3C-PREWARM-TIMEOUT-LEDGER — obligation-4 `cancelled` synthesis at every terminal fan-out exit (DDR §11.5 M2) |
| Committed source | §25.15.2 obligation 4 (the not-yet-dispatched `cancelled` discriminator, v1.32); v1.44 §1 pause semantics (re-scoped at item 4); `.harness/u1-3c-prewarm-design-decision-record.md` §11.5 M2 |
| Disposition | `cancelled` (terminal-only, ledger-only) via the shared `_synthesize_undispatched_terminals()` at 4 terminal exits; PAUSED boundary stays scan-free; 7 new witnesses |
| Decorrelated review | Fable-5 pre-build adversarial design review (advisor + Codex unavailable in bg session, standing fallback per `[[fable5-fallback-reviewer]]`): VERDICT AMEND, 0 blocking; C1 (v1.44 re-scope) / C2 (protocol-not-bound exit) / C3 (dedup residual named + ML7) / C4 (shared helper + handler merge) / C5 (fence-arm liveness documented) all incorporated. Post-build Fable-5 decorrelated diff review: 0 BLOCKING / 2 CONCERN / 1 COSMETIC — all 8 attack points CLEAN (refactor equivalence, handler merge, double-write, crash modes, drain, test pins, cites, types; suites independently re-run); the 2 concerns are the item-6 fence-family findings (prose re-scoped + `B-18-FENCE-LEDGER-FIDELITY` registered); the cosmetic (ML7 hard-coded deadline restore) fixed in-arc |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED. |
| Runtime spec | UNCHANGED |
| Follow-on status | B-18-3C-PREWARM-TIMEOUT-LEDGER CLOSED; B-18-FENCE-LEDGER-FIDELITY registered (item 6); B-18-EPOCH-PARTITION remains open (dedicated session) |
