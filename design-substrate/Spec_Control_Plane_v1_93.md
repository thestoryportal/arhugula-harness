# Spec: Control Plane — v1.93 (delta over v1.92)

*Delta-only file. The v1.92 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-FENCE-LEDGER-FIDELITY-OW bundled-absorption arc: the §25.15.2 obligation-4 ledger-audit scan — landed for PARALLELIZATION at v1.91 (M2) and given its fence-family arms at v1.92 — is extended to the ORCHESTRATOR_WORKERS engine per the v1.92 item-7 registration, honoring O-W's three structural differences (aborted-return bypass; never-landed M2 terminal exits; the third disposition class + O-W's own recovered dicts). Design authority: `.harness/b18-fence-ledger-fidelity-ow-design-decision-record.md` (pre-build Fable-5 adversarial design review: VERDICT AMEND, 0 blocking, all findings folded pre-build).*

## Change-note (v1.92 → v1.93)

**What this fixes.** v1.92 item 7 registered the honest O-W scope: O-W SHARES the zero-footprint ABORT-exit shape (`orchestrator-workers-effect-fence-aborted` fired BEFORE its scan), its obligation-4 scan was an inline CASCADE_CANCEL-only loop (deadline and pause-tier terminal exits never received the v1.91 M2 scan at all), O-W carries a third disposition class (`paused_child_dispositions`), and O-W has its own recovered dicts (`_recovered_effect_fence_paused` + `_recovered_paused_child`). Pre-arc, a worker withheld or stash-parked past any of those exits — and, on a resume round, a snapshot-recovered peer withheld before its re-dispatch — left ZERO ledger footprint at a terminal exit nothing resumes, or (at the inline scan) a recovered-withheld peer would have synthesized the store-contradicting `cancelled`. Store markers, snapshots, operator resume, and crash-resume were and remain honest — this delta is the LEDGER-side repair, mirroring v1.91/v1.92 for the second fan-out engine.

**Scope of revision — §25.17 addendum (ORCHESTRATOR_WORKERS obligation-4 scan):**

1. **The inline loop is FACTORED into an O-W-local `_synthesize_undispatched_terminals()` closure, called at SEVEN terminal exits.** The exits: (i) fence-ABORT (immediately before the `orchestrator-workers-effect-fence-aborted` FAILED return — positioned tier-agnostically, strict-tier-only in practice since PROCEED returns earlier and has no abort catch); (ii) CASCADE_CANCEL post-barrier (the pre-arc inline site, byte-equivalent arms preserved); (iii) PROCEED deadline → PARTIAL (the two deadline handlers merged, M2 parity); (iv) PROCEED paused-child → FAILED `child-paused-not-resumable-under-proceed` (an O-W-specific exit with no parallelization analogue — the stashed child itself is the zero-footprint branch); (v) PAUSE-tier deadline → FAILED `barrier-deadline`; (vi) PAUSE `pause_resumable=False` → FAILED `not-yet-materialized` (defence-in-depth — no live caller passes False; direct-call-reachable only, honestly labeled); (vii) PAUSE protocol-not-bound → FAILED. Run statuses, fail_classes, and exit ORDER are byte-unchanged at every exit.

2. **Six arms, in ORDER** (an aborted ordinal is BY CONSTRUCTION also in the recovered-fence dict — the ABORT directive is built from it — so the aborted arm is checked first, the v1.92 FL7 discipline):
   - **(1) fence-ABORTED** (this-round `EffectFenceAbortedError`): dispatched and REFUSED → ledger `completed` terminal-ONLY, NO step entry, NO store capture (a capture would flip the crash gate's fence-recoverable classification and erase the operator's pending ABORT — the v1.92 item-2 vocabulary verbatim).
   - **(2) fence-paused, THIS round**: `completed` + the durable store capture (the pre-arc CASCADE_CANCEL arm carried unchanged).
   - **(3) fence-paused, RECOVERED** (withheld/lookup-failed this round before its re-dispatch): obligation-4 `completed`, NO capture (the v1.92 item-3 snapshot-carried asymmetry).
   - **(4) paused-child, THIS round**: `completed` (the pre-arc CASCADE_CANCEL arm), NO capture — a capture would flip the crash gate's child-recoverable classification to recovered-terminal, dropping the child snapshot's resumability.
   - **(5) paused-child, RECOVERED**: `completed`, NO capture (the prior snapshot carries it in `paused_child_branches`; the third-disposition-class half of the union arm — `cancelled` would contradict its attempt-1 dispatch marker).
   - **(6) else** never-dispatched → `cancelled`, LEDGER-only (the M2 baseline; dispatch-marker ABSENCE stays the durable provably-never-ran witness).

3. **Named crash-visible additions (the committed v1.65 §1(c) reproduce-the-terminal trade, per the v1.92 item-4 convention).** The fence-this-round capture arm (2) is crash-visible wherever it newly fires: **live-reachable at the fence-ABORT exit** (a this-round INERT re-paused peer under a mixed ABORT map — witness OW1) **and at the protocol-not-bound exit on a fresh run** (witness OW6b); **race-reachable at the PAUSE deadline exit** (a stash-family raise in the watchdog window ends its task CANCELLED, not failed — the identical composition v1.91 item 3 committed as "documented, not discovered"); **direct-call-only at the not-yet-materialized exit**. The byte-identical-crash-resume claim is scoped to the capture-less arms (1/3/4/5), exactly as v1.92 scoped it.

4. **Boundaries deliberately scan-free.** The worker-failure → PAUSED boundary (snapshot OMISSION is the re-dispatchable contract, §25.15.1 — witness OW8b); the resume-rejection guards (pre-flight refusals: the round never released a worker, and the prior snapshot remains the valid resume authority); the `not branch_plan` short-circuit (no plan-carried branches); the orchestrator-region exits (fire before the worker plan exists); the clean-path tail (every stash path re-raises → `worker_failed`, so no plan-carried branch can be stranded there).

5. **Obligation-7 reading restated for O-W** (the v1.91 item-5 / v1.92 item-5 clause, verbatim in force): synthesized ledger terminals are PER-ATTEMPT AUDIT records, not resume authority; re-dispatch eligibility keys on snapshot omission, never on a ledger terminal read — a recovered peer with a synthesized `completed` is legitimately re-dispatched by a later stale-snapshot resume.

6. **Recovered-class reachability at the pause-guard exits (grounded at build).** `execute_workflow` IGNORES `pause_snapshot_input` when no `PauseResumeProtocol` is bound (the resume gate requires the protocol to validate the snapshot; without it the run proceeds FRESH) — so a genuine resume round always has the protocol bound, and the recovered arms (3/5) at exits (vi)/(vii) are reachable only by a direct engine call (`resume_snapshot=` + a protocol-less ctx). The uniform closure is unaffected (an arm never fires where its class cannot exist); the fresh-run classes at those exits are live-reachable (witness OW6b).

7. **The PROCEED paused-child × deadline composition is NAMED (pre-existing, out of scope).** A stash-then-deadline interleaving exits through the merged deadline handler → run PARTIAL (the paused-child FAILED check runs only on the no-timeout path). The scan now records the stashed child's `completed` there (witness OW10); the run-status composition itself is pre-arc behavior this audit-surface-only arc does not change.

8. **HIERARCHICAL_DELEGATION inherits every site per level** (its recursion re-enters `_execute_orchestrator_workers`; zero HD-specific code).

9. **Registered follow-on (pre-build review finding 3): `B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL`.** The reconstruct-no-dispatch × protocol-unbound FAILED path inside the `not branch_plan` block returns BEFORE any snapshot is built, leaving the reconstruct-skipped ordinals (proven not-yet-run) and the carried fence-recoverable ordinals with zero footprint and no snapshot — a genuine residual OUTSIDE this arc's seven exits, SHARED with the committed PARALLELIZATION sibling (whose protocol-not-bound scan call is vacuous over the empty plan on that path; v1.92 did not fix it either). Registered in the arc-ledger with two-engine scope (a `cancelled` synthesis over the skipped ordinals is provably honest there: instrumented + no dispatch marker); deliberately NOT silently widened into this arc.

10. **v1.92 item 7 is discharged.**

**New witnesses** (`harness-cp/tests/test_workflow_driver_orchestrator_workers_fence_ledger.py`; deterministic constructions use the synchronous registry-lookup raise — the poisoned ordinal itself is the zero-footprint branch; a sibling's raise never deterministically cancels later task bodies, verified empirically at build):

| # | Pins |
|---|---|
| OW1 | fence-ABORT exit on a resume round: FAILED `orchestrator-workers-effect-fence-aborted` unchanged; aborted ordinal (∈ aborted ∩ recovered) → `completed` terminal-ONLY no-capture (arm order); suppressed INERT re-paused peer → `completed` + capture (named addition #1); zero step entries / STEP_BOUNDARYs this round |
| OW4 | CASCADE_CANCEL union on a persona-tier-change resume: two recovered fence peers + one recovered paused-child, all lookup-failed → three `completed` capture-less (the third-class union); recovered terminal not re-dispatched; store + markers byte-unchanged |
| OW5 | PROCEED paused-child FAILED exit: the stashed child records `completed` terminal-ONLY capture-less (pre-arc: zero footprint) |
| OW6a | protocol-not-bound union (direct engine call per item 6): same three union-arm records; no snapshot |
| OW6b | protocol-not-bound, fresh run: this-round fence peer `completed` + capture (named addition #2); the plain-failed sibling keeps its own step + `completed` |
| OW8a | containment: fresh CASCADE_CANCEL all-poisoned cell byte-preserves the pre-arc inline outputs (both `cancelled`, resume-ineligible) |
| OW8b | containment: worker-failure → PAUSED stays scan-free on a resume round; the new snapshot's fence set composed from this-round dispositions only; recovered peers re-dispatchable by omission |
| OW9 | not-yet-materialized (direct call; `pause_resumable=False` is the signature default): fence stash `completed` + capture, poisoned sibling `cancelled` |
| OW10 | PROCEED deadline with a stashed paused-child: PARTIAL unchanged; child → `completed` terminal-ONLY; in-flight-cut sibling keeps its own `timed_out` |

**Invariants preserved.** NO §5.2 IS-hash change (ledger terminal Literal unchanged: `cancelled`/`completed`/`timed_out`). NO new contract / ADR / fail-class / enum / CXA edge / snapshot schema change. Run statuses + fail_classes byte-unchanged at every exit. Dispatch markers byte-unchanged; store captures byte-unchanged except the item-3 named additions. `workflow.step_count` / `steps_executed` unaffected (terminal-only entries; the drain predicate counts STEP entries only). First-round + non-fence + non-child paths byte-identical (OW8a; the pre-arc O-W suites green unmodified). PARALLELIZATION engine byte-unchanged. Runtime spec UNCHANGED.

Suite state at close: recorded at the PR (harness-cp full suite + runtime non-e2e + axes green; workspace pyright 0/0/0; ruff clean).

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-FENCE-LEDGER-FIDELITY` | Fence-state × terminal-exit audit records (PARALLELIZATION; v1.91 item 6a/6b) | CLOSED (v1.92) |
| `B-18-FENCE-LEDGER-FIDELITY-OW` | O-W aborted-return bypass + never-landed M2 terminal exits + union arm (three-class arms) | **CLOSED (this arc)** |
| `B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL` | Shared two-engine reconstruct-no-dispatch × protocol-unbound zero-footprint residual (item 9) | **Registered (this arc)** |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition | Registered, open (dedicated session) |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_93.md` (delta over v1.92) |
| Arc | B-18-FENCE-LEDGER-FIDELITY-OW — the obligation-4 scan extended to ORCHESTRATOR_WORKERS (v1.92 item 7 discharge) |
| Committed source | §25.15.2 obligations 3/4/7 (v1.32); v1.65 §1; v1.73/v1.74 §1 (abort-family recording split); v1.91 items 2/3/5 (M2 scan + per-attempt clause + race characterization); v1.92 items 1–7; `.harness/b18-fence-ledger-fidelity-ow-design-decision-record.md` |
| Disposition | Factored scan at SEVEN O-W terminal exits; six arms aborted-first; union arm over BOTH recovered dicts (`completed` capture-less); paused-child arms capture-less; named crash-visible additions per item 3; PAUSED/rejection/empty-plan boundaries scan-free; HD inherits per level |
| Decorrelated review | Fable-5 pre-build adversarial design review (advisor unavailable + Codex TLS-blocked in bg session, standing fallback per `[[fable5-fallback-reviewer]]`): VERDICT AMEND, 0 blocking / 4 concern / 3 cosmetic — all folded into the DDR pre-build (E3 reachability {1,4,6} + OW10; E5 race pin re-worded per the v1.91 item-3 characterization; the reconstruct residual REGISTERED not absorbed; invariant-3 capture-reachability re-scope; witness mechanics named; cite fix; E1 tier wording). Post-build decorrelated diff review recorded at the clearance marker. |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED. |
| Runtime spec | UNCHANGED |
| Follow-on status | B-18-FENCE-LEDGER-FIDELITY-OW CLOSED; B-18-FENCE-LEDGER-RECONSTRUCT-RESIDUAL registered (item 9); B-18-EPOCH-PARTITION remains open (dedicated session) |
