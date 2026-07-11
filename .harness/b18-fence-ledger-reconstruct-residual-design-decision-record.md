# B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL — Design Decision Record

*Pre-build design packet for the two-engine reconstruct-no-dispatch × protocol-unbound zero-footprint residual (skipped-ordinal `cancelled` synthesis). Registered at CP spec v1.93 item 9 (the -OW pre-build review finding 3); arc row at `.harness/arc-ledger.yaml` (`B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL`, registered, decompose-at-open). Authored 2026-07-11 at arc open; session posture: Phase 7 bundled-absorption (CP spec delta + harness-cp impl co-land, clearance marker in-PR per CLAUDE.md §11.4).*

---

## 0. Committed authority (what this arc builds against — none of it is re-litigated)

| Authority | Commitment consumed here |
|---|---|
| CP spec §25.15.2 obligation 4 (v1.32) | Every plan-carried branch at a TERMINAL exit has a ledger disposition; `cancelled` = not-yet-dispatched ONLY |
| CP spec v1.90 §25.17 item 4 | Dispatch-marker ABSENCE is the durable provably-never-ran witness; synthesized entries are LEDGER-only, never store writes |
| CP spec v1.91 items 2/3/5 (M2 scan) | Terminal-ONLY entries (no step entry); per-attempt audit records, not resume authority; re-dispatch keys on snapshot omission |
| CP spec v1.92 items 2/3 (fence arms) | Union-arm vocabulary: a recovered/withheld dispatched ordinal takes obligation-4 `completed` CAPTURE-LESS (`cancelled` would contradict its own store; a capture would flip the crash gate's classification) |
| CP spec v1.93 items 1–8 (-OW extension) | The seven-exit O-W scan + six arms; item 4 lists the `not branch_plan` short-circuit scan-free (no plan-carried branches) — and the SEPARATE item 9 registers the reconstruct × protocol-unbound residual inside that block as this arc's scope (review RR-3: two sentences, not one) |
| CP spec v1.93 item 9 | THIS arc's registration: the reconstruct × protocol-unbound FAILED path returns before any snapshot is built; skipped + carried ordinals end zero-footprint at an exit OUTSIDE the plan-driven scans; SHARED with the parallelization sibling (vacuous scan over the empty plan) |
| CP spec v1.70 §1 / v1.71 §1 | The reconstruct-no-dispatch classification: NOT-YET-DISPATCHED (instrumented + no marker) and RE-FIRE-SAFE MAYBE-RAN (marker, no capture, DECLARATIVE/INFERENCE) are OMITTED from the plan; FENCE-RECOVERABLE MAYBE-RAN is CARRIED as `EffectFencePausedBranchResumeState` |
| v1.68 §1 re-establish | The protocol-BOUND leg re-pauses (PAUSED + snapshot omitting the skipped) — that leg is CORRECT and untouched: omission IS the re-dispatchable contract |

## 1. The defect (grounded at HEAD `15c9f5ae`)

On a **crash-resume** (`crash_fan_out_resume` threaded, `resume_snapshot is None`) under `CascadePolicy.PAUSE` with a pause trigger and an **incomplete** recovery whose absent ordinals are all provably safe, the driver enters **reconstruct-no-dispatch mode** (`workflow_driver.py:3345-3370`): `crash_pause_reconstruct_no_dispatch=True` + the fence-recoverable ordinals carried as `crash_pause_reconstruct_fence_paused`. Both engines then skip EVERY non-recovered ordinal at plan build (parallelization `:7010-7011`; O-W `:9837-9838`) → `branch_plan` is empty.

At the re-establish gate, the **protocol-unbound** leg returns a terminal FAILED **before any snapshot is built**:

- **PARALLELIZATION** `:8115-8132` — `_crash_pause_reestablish` true → `protocol is None` → the existing obligation-4 scan call at `:8127` runs but is **vacuous** (the scan closure iterates `branch_plan`, `:7570`) → FAILED `parallelization-pause-resume-protocol-not-bound`.
- **ORCHESTRATOR_WORKERS** `:10234-10256` — `_crash_pause_trigger` gate → `_reestablish_protocol is None` → **no scan at all** → FAILED `orchestrator-workers-pause-resume-protocol-not-bound`.

Ledger state at that exit: the recovered terminals ARE re-materialized (the B-FANOUT-OUTPUT-REPLAY seed loops, parallelization `:7244-7276`, O-W `:10032-10065`) — but the **reconstruct-skipped ordinals and the carried fence-recoverable ordinals have ZERO ledger footprint**, at a terminal exit nothing resumes (FAILED; no snapshot; the re-dispatchable-by-omission defense applies only to a PAUSED snapshot). Store markers/snapshots stay honest — this is the LEDGER-side audit gap, the exact v1.91 item-2(d) rationale at the one exit the M2/v1.92/v1.93 plan-driven scans structurally cannot reach.

**Production reachability.** A PAUSE-tier manifest deployed without the pause-resume protocol stage: crash mid-fan-out (a branch had failed) → operator re-runs → reconstruct mode → protocol-not-bound → FAILED with the skipped ordinals ledger-invisible. No direct-call contrivance needed (unlike the v1.93 item-6 pause-guard recovered arms).

## 2. Ordinal classes at the exit — the THREE-arm decomposition

Decompose-at-open discovery (extends the item-9 registration's two-class vocabulary honestly, the #930 "build-time discovery folded" pattern): the reconstruct-skipped set contains **two** distinct classes, because v1.71 admits re-fire-safe maybe-ran ordinals into reconstruct mode:

| Class | Membership (driver-side, `:3267-3370`) | Store state | Honest disposition |
|---|---|---|---|
| (a) carried fence-recoverable | `crash_pause_reconstruct_fence_paused` (= `_pr_maybe_ran_unsafe − _pr_fence_unrecoverable`; reconstruct requires `_pr_fence_unrecoverable = ∅`, so = the re-fire-unsafe maybe-ran) | marker PRESENT, no capture, reserve held | `completed` terminal-ONLY, **capture-less** (v1.92 union-arm verbatim: attempt-1 dispatched; `cancelled` contradicts the marker; a capture orphans the reserve + flips a future reconstruct's classification) |
| (b) re-fire-safe maybe-ran | `_pr_maybe_ran − _pr_maybe_ran_unsafe` (DECLARATIVE_STEP / INFERENCE_STEP; marker present, no capture) — **currently carried NOWHERE** | marker PRESENT, no capture | `completed` terminal-ONLY, **capture-less** (obligation-4 forecloses `cancelled` — the dispatch fired; a `completed` capture would flip a future reconstruct's `_crash_pause_trigger`/maybe-ran classification — the v1.92 aborted-arm capture-NOT reasoning) |
| (c) not-yet-dispatched | remainder: instrumented + NO dispatch marker | marker ABSENT | `cancelled` terminal-ONLY, LEDGER-only (the M2 baseline; marker-absence stays the durable provably-never-ran witness) |

Excluded: recovered-terminal ordinals (already re-materialized, have footprint); the orchestrator itself (O-W: its own step/ledger handling is the orchestrator region, out of scope); scoped-abort ordinals (recorded durably at their own block — and structurally absent in reconstruct mode: no resume context).

**No step entries anywhere** (a step entry would claim a step ran THIS attempt — classes (a)/(b) dispatched in the CRASHED attempt, class (c) never). **No store writes anywhere** — every arm is store-inert, so the byte-identical-crash-re-run claim covers the WHOLE synthesis (this arc has **zero named crash-visible additions**, unlike v1.92/v1.93 which each named capture arms).

## 3. Design decisions

**DD-1 — Thread the classification; do not re-derive it engine-side.** The driver already classified every ordinal (`:3267-3370`). Add ONE param to both engine signatures + the three strategy call sites (`:3675-3679`, `:3724-3728`, `:3757-3761`) and the HD pass-through (`:11255-11258`):

```python
crash_pause_reconstruct_refire_safe: frozenset[int] = frozenset()
```

populated in reconstruct mode with `_pr_maybe_ran − _pr_maybe_ran_unsafe` (driver local initialized beside the `:2876`/`:2883` reconstruct locals). Engine-side: class (a) = carried tuple's `branch_index`es; class (b) = the new frozenset; class (c) = the per-engine ordinal domain − recovered-terminal − (a) − (b), where the domain is **`range(len(steps))` for PARALLELIZATION and `range(len(worker_steps))` for O-W** (0-based worker ordinals; `worker_steps = steps[1:]`; synthesized O-W child contexts carry `step_index = bi + 1` per the `:10047` seed convention — review RR-2). Single source of truth (the driver's one store read); a second engine-side store read could diverge mid-run and would put two authorities on one classification.

**THE GATE (review RR-1 — the packet's load-bearing amendment).** The reconstruct arms — including the class-(c) derivation — are **structurally gated on `crash_pause_reconstruct_no_dispatch=True`**. They are NOT "incidentally empty" off-mode: on a fresh run recovered-terminal = ∅, so an ungated (c) would equal ALL ordinals and the shared closures would synthesize a phantom `cancelled` per live branch at every one of the 12 existing terminal-exit call sites (violating the FL6 exactly-one-terminal pin + the OW8a/ML6 byte-preservation invariants). Off-mode the arms are skipped by the gate, structurally; in-mode the plan is empty (`:7010-7011`, `:9837-9838`) so plan-carried ∩ (c) = ∅ by construction. The RR5/containment controls pin the gate, not an emptiness accident.

**DD-2 — Placement: extend the shared scan closures with reconstruct arms; O-W gains its EIGHTH call site.**
- PARALLELIZATION: the reconstruct arms live in `_synthesize_undispatched_terminals` (`:7569`) AFTER the existing plan loop. At every non-reconstruct exit the three sets are empty → byte-identical behavior at all five existing call sites. The `:8127` protocol-not-bound call — today vacuous under reconstruct — becomes the synthesis site with **zero new call sites**.
- O-W: same closure extension (`:10483`) + ONE new call at the reconstruct protocol-unbound exit (before the `:10248` FAILED return). The closure is defined AFTER that exit in the function body — **the def moves above the `not branch_plan` block**; Python late binding keeps the existing seven call sites' semantics (all closed-over names are bound before every call site executes; the suite is the check).
- Writer mechanics: synthesized ordinals have no plan writers. Compose child contexts + writers exactly like the re-materialization seed loops (parallelization `:7253-7263` — no step_index override; O-W `:10041-10052` — `step_index=bi+1`), append the terminal entry, then: parallelization appends the writers to `branch_writers` (drained by `_finish` at `:7410`; `_writer_ran_a_step` false for terminal-only → `steps_executed` + STEP_BOUNDARY counts unchanged); O-W drains the synthesized writers explicitly at the exit via `_drain_and_emit_step_boundaries` (returns 0 for terminal-only → `_reestablish_steps` unchanged).
- Ordering (review RR-6): parallelization is correct only because the scan call at `:8127` PRECEDES the `_finish` drain (`:8128` → `:7410`) — append-then-drain; O-W's explicit drain of the synthesized writers runs AFTER the `:10193` recovered-writer drain and BEFORE the `:10248` FAILED return.
- Closure-def placement (review Q2, verified name-by-name): the O-W def moves to immediately above the `not branch_plan` block, after the scoped-abort recording block — every closed-over name of the current body AND of the reconstruct extension (worker_steps `:9259`, fanout_parent `:9806`, branch_writers `:9957`, the recovered dicts, the disposition dicts, the new params) is assigned strictly before `:10184`.

**DD-3 — Scope: the protocol-UNBOUND leg only.** The protocol-bound leg re-establishes PAUSED with the snapshot omitting the skipped ordinals — omission is the re-dispatchable contract (§25.15.1); synthesizing terminals there would contradict re-dispatch eligibility semantics for a live resume surface. Scan-free stays CORRECT there (witness RR2/RR4 pin it). Also untouched: the complete-recovery `not branch_plan` legs (skipped/carried/refire-safe sets all empty → the new arms are vacuous → byte-preserved, witness RR5), the resume-rejection guards, the PAUSED worker-failure boundary, the requires-strict-tier pre-flight refusals (prior snapshot remains the valid resume authority — v1.93 item 4 verbatim).

**DD-4 — Run statuses, fail_classes, exit order, return-value step counts: byte-unchanged at both exits.** The synthesis inserts ledger records only. `workflow.step_count` / `steps_executed` unaffected (terminal-only; the drain predicate counts STEP entries, `:6233-6246`).

**DD-5 — Obligation-7 clause restated.** Synthesized terminals are PER-ATTEMPT AUDIT records. A later re-run of the same key re-enters reconstruct (store byte-unchanged) and may synthesize again — branch-terminal idempotency dedups within a ledger; the committed C3/ML7 per-attempt residual shape carries verbatim. Re-dispatch eligibility never reads a ledger terminal.

**DD-6 — Spec delta CP v1.93→v1.94** discharges item 9: the two exits, the three arms (naming the class-(b) build-time discovery), the RR-1 reconstruct-mode gate, store-inert/no-named-additions, the PAUSED-leg + complete-recovery boundaries stay scan-free, HD inherits (recursion re-enters O-W; zero HD-specific code), obligation-7 restated. **Two explicit supersessions of committed v1.93 sentences (review RR-3, the v1.92 item-6 re-scope precedent):** (i) item 1's "called at SEVEN terminal exits" → EIGHT O-W call sites (the reconstruct × protocol-unbound exit added); (ii) item 4's scan-free list row "the `not branch_plan` short-circuit (no plan-carried branches)" → superseded to name the exception: scan-free EXCEPT the reconstruct × protocol-unbound exit, whose synthesis is the item-9 discharge (the rest of the block — complete-recovery legs, PROCEED gate, re-establish-PAUSED — stays scan-free). Clearance marker + arc-ledger row close (registered 2→1) in-PR. No new contract / ADR / fail-class / enum / IS-hash / CXA / snapshot-schema change; runtime spec UNCHANGED.

## 4. Witnesses (all fails-on-main BY EXECUTION except the designed controls)

Deterministic construction: a real crash-attempt run under PAUSE writes the store (markers + captures + a genuine branch failure), then the resume attempt runs against a protocol-less ctx — the organic two-run shape (`[[full-chain-witness-not-half-proofs]]`).

| # | Engine | Pins | Expect on main |
|---|---|---|---|
| RR1 | PARALLELIZATION | reconstruct × unbound: FAILED `parallelization-pause-resume-protocol-not-bound` unchanged; recovered ordinal re-materialized; carried fence ordinal `completed` capture-less; refire-safe maybe-ran `completed` capture-less; not-yet-dispatched `cancelled`; NO step entries for synthesized ordinals; store byte-unchanged (markers/captures identical pre/post) | FAIL (zero footprint for the three) |
| RR2 | PARALLELIZATION | same construction, protocol BOUND → PAUSED + snapshot omitting skipped; **NO synthesized terminals** (scan-free leg preserved) | PASS (byte-preservation control) |
| RR3 | O-W | the RR1 mirror: FAILED `orchestrator-workers-pause-resume-protocol-not-bound` unchanged; same three arms + re-materialized recovered; `_reestablish_steps` return unchanged | FAIL |
| RR4 | O-W | the RR2 mirror (protocol bound → re-established PAUSED; scan-free) | PASS (control) |
| RR5 | either | complete-recovery reconstruct (`not branch_plan` via all-recovered) × unbound → the pre-arc FAILED outputs byte-preserved (empty synthesis) | PASS (containment control) |
| RR6 | either | store-inertness via OBSERVABLES (review RR-5/Q3 — never `_pr_*` internals): after RR1's FAILED attempt-1, (i) store byte-equality pre/post attempt-1; (ii) attempt-2 reproduces the same fail_class + the same per-attempt synthesized multiset; (iii) binding the protocol on attempt 3 re-pauses properly (the honest recovery path unbroken). Cross-attempt ledger dedup asserted ONLY if one ledger threads both attempts (branch-terminal idempotency → first-attempt-standing, the ML7 shape); per-attempt fresh ledgers each carry their own copy | FAIL on (i)/(ii) if any arm wrote the store |
| RR7 | either | the obligation-7 leg for the NEW shape (review RR-5): after attempt-3's re-established PAUSED, `api.resume` genuinely RE-DISPATCHES a class-(b)/(c) ordinal despite attempt-2's synthesized ledger terminal — extends ML7's synthesized-`cancelled` coverage to marker-bearing synthesized-`completed`; re-dispatch keys on snapshot omission, never a ledger terminal read | FAIL if resume eligibility ever reads the synthesized terminal |

Suite home: a new `test_workflow_driver_fanout_reconstruct_residual_ledger.py` beside the FL/OW fence-ledger suites (shared fixture vocabulary), determinism-repeat per suite convention.

## 5. Invariants preserved (the checklist the reviews audit)

NO §5.2 IS-hash change (ledger terminal Literal unchanged). NO new contract/ADR/fail-class/enum/CXA edge/snapshot schema. Run statuses + fail_classes + exit order byte-unchanged. Dispatch markers + store captures byte-unchanged (zero store writes — stronger than v1.92/v1.93, which each named additions). `workflow.step_count`/`steps_executed` unaffected. First-round + non-crash + snapshot-resume paths byte-identical **because the reconstruct arms are structurally GATED on `crash_pause_reconstruct_no_dispatch=True` (review RR-1) — not because the sets happen to be empty**; the five parallelization + seven O-W existing scan sites are byte-equivalent off-mode by that gate. PAUSED boundaries stay scan-free. Runtime spec UNCHANGED.

## 6. Open questions — RESOLVED at the pre-build review (Fable-5, VERDICT AMEND 0 blocking / 5 concern / 2 cosmetic, 2026-07-11; all findings folded above)

1. **Arm-(b) disposition: `completed` capture-less CONFIRMED.** Obligation-4's discriminator forecloses `cancelled` (the maybe-ran set is *defined* by marker presence); `timed_out` foreclosed (nothing deadline-cut it); ledger-SILENT would recreate the item-9 defect in worse form — v1.91 item 2(d) commits that without a snapshot, zero footprint is "systematically indistinguishable from lost entries", and the unbound exits return before any snapshot exists. The bound-leg mirror is a category error: omission there is a live re-dispatch contract on a resume surface; the unbound leg is a terminal audit surface.
2. **Closure-def move VERIFIED SAFE by name-by-name enumeration** (see DD-2 placement bullet). Suite is the residual check.
3. **RR6 pin shape settled** (see the RR6 witness row): observables only — store byte-equality + per-attempt fail_class/multiset; cross-attempt dedup asserted only on a shared-ledger thread; plus the NEW RR7 obligation-7 leg.

## 7. Witness crash-construction mechanics (review RR-4; the -OW DDR §7 discipline)

The two-run organic construction uses the v1.70/v1.71 reconstruct suites' ESTABLISHED store levers (`harness-cp/tests/test_workflow_driver_fanout_output_replay_full_chain.py` — `_InMemoryBranchStore` + `_run_persona` + `_CountingDispatcher` + `_pause_protocol`, with `_RecordingLedger`/`_Ctx`/`_completed_branch_indexes` for the ledger assertions; O-W via `_manifest(topology=TopologyPattern.ORCHESTRATOR_WORKERS)`):

- **Run-1 (the crashed attempt)** dispatches all branches under PAUSE with `fail_index` on one branch → a genuine captured failure (the pause trigger; ran-and-errored, `completed` + no output).
- **Class (c)** not-yet-dispatched: `store.forget_branch_undispatched(key, i)` — drops marker AND capture, leaves the run instrumented (the `test_crash_resume_pause_not_yet_dispatched_*` lever, `:3841-3846`).
- **Class (b)** re-fire-safe maybe-ran: `store.forget_branch(key, i)` on a DECLARATIVE/INFERENCE ordinal — capture dropped, marker KEPT (the `:3428` lever).
- **Class (a)** fence-recoverable maybe-ran: `store.forget_branch(key, i)` on a TOOL_STEP ordinal (marker kept, kind TOOL → re-fire-unsafe → fence-recoverable; the #742 fence-step-id witnesses' construction, `:4096` region).
- **Run-2 (the resume attempt)**: same workflow/store, NO `pause_resume_protocol` → the protocol-unbound reconstruct exit (RR1/RR3), or protocol bound (RR2/RR4 controls). A raise-based failure CANNOT fabricate the maybe-ran window (it records ran-and-errored, captured) — the store levers are the honest mechanism, matching how the committed reconstruct witnesses model the crash.

## 8. Build-notes addendum (2026-07-11, at build close)

1. **Witness home deviation from §4.** The RR witnesses landed IN `test_workflow_driver_fanout_output_replay_full_chain.py` (with a one-param `_run_persona` extension: optional `ledger`), NOT the §4-anticipated new file — the two-run crash construction, `_InMemoryBranchStore` levers, `_RecordingLedger`, and O-W topology runner all live there; a parallel file would have duplicated ~200 lines of harness for zero isolation gain.
2. **RR6+RR7 merged into one witness** (`test_reconstruct_residual_store_inert_per_attempt_then_recovers`) — attempt-1/attempt-2 unbound (store byte-equality + per-attempt fail_class/multiset equality), attempt-3 bound (PAUSED re-establish unbroken), attempt-4 `api.resume` (the obligation-7 re-dispatch of the omitted + carried ordinals despite attempt-2's synthesized terminals). 6 test functions total.
3. **Fails-on-main BY EXECUTION: 2/6** — RR1 (KeyError on the class-(b) ordinal: zero footprint) + RR3 (the O-W mirror) fail at a throwaway main worktree; RR2/RR4/RR5/RR6+7 pass there as DESIGNED byte-preservation/invariant controls (RR6+7's new-shape halves are only exercisable on the branch; its main-pass is the trivial no-synthesis instance).
4. **No further empirical corrections** — the reviewed design built as specified: the RR-1 gate, the threaded refire-safe carrier, the O-W closure-def move (suite-verified: 1524 harness-cp green incl. all 7 pre-existing O-W scan-site witnesses), the per-engine domains, and the drain orderings all landed without deviation. Suite state: harness-cp 1524 (+6) / runtime non-e2e 2360 / axes 1590; pyright 0/0/0 (changed files); ruff clean; overlay 357 nodes 31/31 seams.
