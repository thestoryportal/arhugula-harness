# Spec: Control Plane — v1.94 (delta over v1.93)

*Delta-only file. The v1.93 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL bundled-absorption arc: the §25.15.2 obligation-4 scan — landed for PARALLELIZATION at v1.91 (M2), given its fence-family arms at v1.92, extended to ORCHESTRATOR_WORKERS at v1.93 — gains its reconstruct arms at the shared two-engine crash-reconstruct × protocol-unbound terminal exit, discharging the v1.93 item-9 registration. Design authority: `.harness/b18-fence-ledger-reconstruct-residual-design-decision-record.md` (pre-build Fable-5 adversarial design review: VERDICT AMEND, 0 blocking / 5 concern / 2 cosmetic, ALL folded pre-build).*

## Change-note (v1.93 → v1.94)

**What this fixes.** v1.93 item 9 registered the honest residual: on a crash-resume under `CascadePolicy.PAUSE` whose incomplete recovery is provably safe (reconstruct-no-dispatch mode, v1.70/v1.71), both fan-out engines empty their `branch_plan` — so at the protocol-unbound FAILED exit (`parallelization-pause-resume-protocol-not-bound` / `orchestrator-workers-pause-resume-protocol-not-bound`), reached BEFORE any snapshot is built, the reconstruct-skipped ordinals and the carried fence-recoverable ordinals ended with ZERO ledger footprint at a terminal exit nothing resumes. The PARALLELIZATION exit's scan call was vacuous over the empty plan; the O-W exit (inside the `not branch_plan` block) had no scan at all. Store markers, snapshots, and the bound-leg re-establish were and remain honest — this is the LEDGER-side repair, the v1.91 item-2(d) rationale ("without a snapshot the re-dispatchable-by-omission defense does not apply; zero footprint is systematically indistinguishable from lost entries") applied at the one exit the plan-driven scans structurally cannot reach.

**Scope of revision — §25.17 addendum (reconstruct-residual arms):**

1. **The reconstruct arms are added to both engines' shared scan closures, structurally GATED on the reconstruct mode** (`crash_pause_reconstruct_no_dispatch=True`). Off-mode the arms are skipped by the gate — NOT incidentally empty: an ungated domain-minus-recovered derivation would synthesize a phantom `cancelled` per live branch at every pre-existing terminal exit on a fresh run. In-mode the plan is empty by construction (the reconstruct plan-build `continue`), so the plan loop is vacuous and only the reconstruct arms fire — at the single reconstruct-reachable exit, the protocol-unbound FAILED return (cascade_policy is pinned PAUSE by the driver gate; nothing dispatches, so the deadline / fence-ABORT / CASCADE_CANCEL exits are unreachable).

2. **THREE ordinal classes, decomposed at arc-open** (the registered two-class vocabulary honestly extended — v1.71 admits a class the registration did not name):
   - **(a) carried fence-recoverable** (`crash_pause_reconstruct_fence_paused`; dispatch marker + held reserve): obligation-4 `completed`, terminal-ONLY, NO capture — `cancelled` would contradict the branch's own store; a capture would orphan the reserve and flip a future reconstruct's classification (the v1.92 item-3 vocabulary verbatim).
   - **(b) re-fire-safe maybe-ran** (NEW `crash_pause_reconstruct_refire_safe` carrier; dispatch marker, no capture, DECLARATIVE_STEP / INFERENCE_STEP): obligation-4 `completed`, terminal-ONLY, NO capture — the same marker-presence foreclosure of `cancelled`; a `completed` capture would flip a future reconstruct's `_crash_pause_trigger` / maybe-ran classification.
   - **(c) not-yet-dispatched** (instrumented + NO dispatch marker): `cancelled`, terminal-ONLY, LEDGER-only — the M2 baseline; marker ABSENCE stays the durable provably-never-ran witness.
   Recovered-terminal ordinals are excluded (the B-FANOUT-OUTPUT-REPLAY seed loops already re-materialize them with full footprint). NO step entries anywhere (classes (a)/(b) dispatched in the CRASHED attempt, not this one; class (c) never dispatched).

3. **The classification is THREADED, not re-derived.** One new engine/driver parameter (`crash_pause_reconstruct_refire_safe: frozenset[int]`, populated with `maybe_ran − maybe_ran_unsafe` at the driver's reconstruct gate) joins the two existing reconstruct carriers at the three strategy call sites + the HIERARCHICAL_DELEGATION per-level pass-through. The driver's ONE store read remains the sole classification authority — an engine-side re-read would put two authorities on one classification. Per-engine ordinal domain: `range(len(steps))` for PARALLELIZATION; `range(len(worker_steps))` (0-based worker ordinals) for O-W, synthesized worker contexts carrying `step_index = ordinal + 1` per the seed-loop convention.

4. **ZERO store writes — the whole synthesis is store-inert** (stronger than v1.92/v1.93, which each named capture additions): no `_mark_branch_dispatched`, no `_capture_branch_terminal`, no `record_branch`. A later re-run of the same key re-enters reconstruct with a byte-identical classification; binding the protocol on a later attempt re-establishes PAUSED exactly as before (the honest recovery path unbroken). There are NO named crash-visible additions in this arc.

5. **Two committed v1.93 sentences SUPERSEDED** (the v1.92 item-6 re-scope precedent):
   - v1.93 item 1's "called at SEVEN terminal exits" → **EIGHT** O-W call sites: the crash-reconstruct × protocol-unbound exit inside the `not branch_plan` block is the eighth (the closure def moved above that block; late binding preserves the seven pre-existing sites, verified name-by-name at the pre-build review).
   - v1.93 item 4's scan-free list row "the `not branch_plan` short-circuit (no plan-carried branches)" → scan-free EXCEPT the reconstruct × protocol-unbound FAILED exit (this discharge); the block's other legs — complete-recovery folds, the PROCEED strict-tier gate, the re-establish-PAUSED return — stay scan-free.

6. **Boundaries deliberately scan-free (restated + pinned).** The protocol-BOUND reconstruct leg (re-establish PAUSED: snapshot omission IS the re-dispatchable contract, §25.15.1 — witnesses RR2/RR4); the complete-recovery legs (the reconstruct gate is never set on a complete recovery — witness RR5); the resume-rejection guards; the worker-failure → PAUSED boundary. PARALLELIZATION keeps five scan sites (the protocol-unbound site now carries the reconstruct arms); drain mechanics unchanged (synthesized writers join the `_finish` drain at PARALLELIZATION / drain explicitly before the O-W return; terminal-only writers contribute zero to `steps_executed` / STEP_BOUNDARY — the step-entry drain predicate).

7. **Obligation-7 reading restated** (v1.91 item 5 / v1.92 item 5 / v1.93 item 5, verbatim in force, now extended to marker-bearing synthesized-`completed`): synthesized ledger terminals are PER-ATTEMPT AUDIT records, never resume authority — re-dispatch eligibility keys on snapshot omission. Witness RR7 pins a genuine `api.resume` re-dispatch of class-(b)/(c)/(a) ordinals despite a prior attempt's synthesized terminals.

8. **Production reachability.** A PAUSE-tier manifest deployed without the pause-resume protocol stage: crash mid-fan-out (a branch had failed) → re-run → reconstruct mode → protocol-unbound exit. No direct-call contrivance (unlike the v1.93 item-6 pause-guard recovered arms).

9. **v1.93 item 9 is discharged.**

**New witnesses** (`harness-cp/tests/test_workflow_driver_fanout_output_replay_full_chain.py`, beside the committed reconstruct witnesses whose store levers they reuse — `forget_branch` = maybe-ran, `forget_branch_undispatched` = provably-not-run; build-time note: the witnesses live in the full-chain suite, NOT the DDR §4's anticipated new file, because the two-run crash construction + `_InMemoryBranchStore` harness live there — creating a parallel file would have duplicated the harness):

| # | Pins | On main |
|---|---|---|
| RR1 | PARALLELIZATION reconstruct × unbound: FAILED fail_class byte-unchanged; recovered {0,1} re-materialized; class (b) `completed` + class (a) `completed` + class (c) `cancelled`, all terminal-ONLY (no step entries); store byte-unchanged (deep-equality pre/post) | **FAILS** (zero footprint) |
| RR2 | the bound leg re-establishes PAUSED: skipped ordinals OMITTED from the snapshot, fence ordinal carried, NO synthesized terminals | passes (control) |
| RR3 | the O-W mirror of RR1 at the EIGHTH scan site | **FAILS** (the exit had no scan) |
| RR4 | the O-W bound-leg mirror of RR2 (`fan_out_resume` carrier) | passes (control) |
| RR5 | complete-recovery × unbound: the reconstruct GATE is off on this leg → re-materialized entries only, byte-preserved (containment control; the gate itself is pinned by the 12 pre-existing scan-site suites' exact-list asserts — post-build review RR-D2) | passes (control) |
| RR6+RR7 | store-inertness via observables (per-attempt fail_class + synthesized-multiset equality off a byte-identical store), attempt-3 bound → PAUSED unbroken, then `api.resume` re-dispatches the omitted + carried ordinals despite attempt-2's synthesized terminals (obligation-7 for the new shape) | passes (invariant control) |

Fails-on-main verified BY EXECUTION at a throwaway main worktree: 2/6 fail exactly at the defect (RR1 KeyError on the class-(b) ordinal; RR3 KeyError on the O-W mirror), 4/6 designed controls pass.

**Invariants preserved.** NO §5.2 IS-hash change (ledger terminal Literal unchanged: `cancelled`/`completed`/`timed_out`). NO new contract / ADR / fail-class / enum / CXA edge / snapshot schema change. Run statuses, fail_classes, exit order, and return-value step counts byte-unchanged at both exits. Dispatch markers + store captures byte-unchanged (zero store writes). `workflow.step_count` / `steps_executed` unaffected (terminal-only entries; the drain predicate counts STEP entries only). First-round + non-crash + snapshot-resume + complete-recovery paths byte-identical (the item-1 gate; witnesses RR2/RR4/RR5 + the pre-existing suites green unmodified). Runtime spec UNCHANGED.

Suite state at close: recorded at the PR (harness-cp full suite + runtime non-e2e + axes green; workspace pyright 0/0/0; ruff clean).

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-FENCE-LEDGER-FIDELITY` | Fence-family arms (PARALLELIZATION; v1.91 item 6a/6b) | CLOSED (v1.92) |
| `B-18-FENCE-LEDGER-FIDELITY-OW` | O-W seven-exit extension + union arms | CLOSED (v1.93) |
| `B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL` | Shared two-engine reconstruct × protocol-unbound residual (v1.93 item 9) | **CLOSED (this arc)** |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition | Registered, open (dedicated session) |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_94.md` (delta over v1.93) |
| Arc | B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL — reconstruct × protocol-unbound obligation-4 synthesis (v1.93 item 9 discharge) |
| Committed source | §25.15.2 obligations 3/4/7 (v1.32); v1.68 §1 / v1.70 §1 / v1.71 §1 (the reconstruct family); v1.90 §25.17 item 4; v1.91 items 2/5; v1.92 items 2/3; v1.93 items 1/4/9; `.harness/b18-fence-ledger-reconstruct-residual-design-decision-record.md` |
| Disposition | Reconstruct arms in both shared scan closures, gated on reconstruct mode; three classes (a)/(b)/(c) per item 2; NEW `crash_pause_reconstruct_refire_safe` threaded carrier; EIGHTH O-W call site (def moved above the `not branch_plan` block); zero store writes; PAUSED/bound/complete-recovery legs scan-free |
| Decorrelated review | Fable-5 pre-build adversarial design review (advisor unavailable in bg session, standing fallback per `[[fable5-fallback-reviewer]]`): VERDICT AMEND, 0 blocking / 5 concern / 2 cosmetic — ALL folded pre-build (RR-1 reconstruct gate; RR-2 per-engine domains; RR-3 the two supersessions at item 5; RR-4 witness mechanics section; RR-5 RR6-observables + the RR7 obligation-7 leg; RR-6/RR-7 cosmetic). Post-build decorrelated diff review recorded at the clearance marker. |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED. |
| Runtime spec | UNCHANGED |
| Follow-on status | B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL CLOSED; B-18-EPOCH-PARTITION remains open (dedicated session) |
