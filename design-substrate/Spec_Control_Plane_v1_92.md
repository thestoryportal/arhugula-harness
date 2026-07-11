# Spec: Control Plane — v1.92 (delta over v1.91)

*Delta-only file. The v1.91 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-FENCE-LEDGER-FIDELITY bundled-absorption arc: the two fence-family audit-fidelity findings deliberately registered out-of-scope at v1.91 item 6 are now FIXED — the obligation-4 scan runs at the fence-ABORT terminal exit (the FIFTH exit) with a dedicated aborted arm, and the scan's fence arm consults the UNION of this-round and snapshot-recovered fence peers. Design authority: `.harness/b18-fence-ledger-fidelity-design-decision-record.md` (pre-build Fable-5 adversarial design review: VERDICT AMEND, 0 blocking, all findings folded).*

## Change-note (v1.91 → v1.92)

**What this fixes.** v1.91 item 6 registered two audit-surface defects on compound fence × warm-up × deadline paths: (a) the tier-agnostic `parallelization-effect-fence-aborted` FAILED return fires BEFORE every obligation-4 scan site, so under warm-up a Phase-1 `EffectFenceAbortedError` left the ABORTED branch and ALL withheld siblings with zero ledger footprint; (b) the scan's fence arm keyed on this-round `effect_fence_paused_dispositions` only, so a snapshot-carried recovered fence peer (`_recovered_effect_fence_paused`) withheld on a resume round synthesized `cancelled` — contradicting the §25.15.2 obligation-4 discriminator (`cancelled` ⟹ "not-yet-dispatched boundary, no effectful dispatch"), the branch's own store (attempt-1 dispatch marker present) and its held ambiguous-uncommitted reserve. Store markers, snapshots, operator resume, and crash-resume were and remain honest — this delta is the LEDGER-side repair.

**Scope of revision — §25.17 addendum (fence-state × terminal-exit audit records):**

1. **The scan enumeration is now FIVE terminal exits.** The four v1.91 item-2 exits (CASCADE_CANCEL post-barrier; PROCEED deadline → PARTIAL; PAUSE deadline-strike → FAILED; PAUSE protocol-not-bound → FAILED) plus the fence-ABORT exit: `_synthesize_undispatched_terminals()` now runs immediately before the `parallelization-effect-fence-aborted` FAILED return — a TERMINAL exit nothing resumes. Run status and `fail_class` at that exit are byte-unchanged.

2. **Aborted arm (new, checked FIRST).** An ordinal in `effect_fence_aborted_dispositions` — its this-round re-dispatch met the operator's ABORT directive and the runtime fence raised `EffectFenceAbortedError` — records a ledger `completed` terminal, terminal-ONLY: NO step entry (its dispatch fired but the fence REFUSED the effect — an effectful-step entry would overclaim; obligation 3 targets landed effects), NO store capture (see item 5), NO new fail_class, NO new ledger enum value (`cancelled` is foreclosed by obligation 4 — the branch dispatched; `timed_out` is foreclosed — nothing deadline-cut it; the abort semantics stay carried by the run-level `fail_class` + the durable fence claim, the same "distinguishing value lives elsewhere" split committed for `ABORT_BRANCH` at v1.73 §1 and for the store at v1.74 §1). Arm ORDER is load-bearing: an aborted ordinal also appears in the recovered-fence dict, so the aborted arm precedes the fence-paused union arm.

3. **Fence-paused UNION arm.** The fence arm now consults this-round `effect_fence_paused_dispositions` OR snapshot-recovered `_recovered_effect_fence_paused`:
   - **This-round peer** (unchanged v1.91 item 3 treatment): ledger `completed` + the durable store capture.
   - **Recovered-withheld peer** (new): a previously-fence-paused peer, snapshot-carried, withheld this round before its re-dispatch fired — attempt-1's dispatch fired and holds an ambiguous-uncommitted reserve, which is exactly obligation-4 `completed` ("the branch's in-flight step ran (effect may have landed)"); it records ledger `completed` with **NO store capture**. The capture-or-not question v1.91 item 6 left open is answered CAPTURE-NOT by the snapshot-carried asymmetry: the still-journaled prior snapshot already carries the peer in `effect_fence_paused_branches`, so (i) operator stale-resume resolvability flows from the snapshot alone (the resume skip-set never reads the store), and (ii) capture-less preserves the peer's crash classification byte-exact — marker-present/no-terminal → fence-recoverable MAYBE-RAN → the crash path re-pauses it resolvable, reserve un-orphaned. A `completed` capture would flip it to recovered-terminal and, for a crashed round, trip the `_crash_pause_trigger` completed/no-output key — destroying the peer's crash-path resolvability (a behavior change this audit-surface-only arc forecloses).

4. **The ONE deliberate crash-visible addition (named per the pre-build review, finding 1).** At the NEW fifth exit, a this-round INERT re-paused peer (re-dispatched under a run-level-ABORT suppression, re-raised the fence, then the abort collapsed the round) inherits the v1.91 item-3 arm INCLUDING its store capture. Pre-arc, a crash at that exit classified the peer fence-recoverable MAYBE-RAN (resolvable); post-arc the capture makes it recovered-terminal. This is the committed v1.65 §1(c) trade (reproduce-the-terminal over preserve-resolvability) extended to one more exit — deliberate and witnessed. The byte-identical-crash-resume claim is therefore scoped to the two CAPTURE-LESS arms (items 2 + 3-recovered); everything else about store markers, snapshots, operator resume, and crash-resume is byte-unchanged.

5. **Obligation-7 reading extended explicitly (review finding 6b).** v1.91 item 5's committed clause — synthesized ledger terminals are PER-ATTEMPT AUDIT records, not resume authority; re-dispatch eligibility keys on snapshot omission, never on a ledger terminal read — applies to the synthesized **`completed`** arms exactly as to `cancelled`: a recovered fence peer with a synthesized `completed` is legitimately re-dispatched by a later stale-snapshot resume (the snapshot still carries it; the fence reserve is the at-most-once safety). §25.15.2 obligation 7's literal "reads each branch's persisted terminal_status" wording is superseded for synthesized terminals to exactly this extent (the v1.91 item-5 general clause, restated to foreclose a future literal reading against the `completed` arms).

6. **v1.91 item 6 is discharged.** Finding 6a and 6b are fixed by items 1-3 above; the v1.91 prose scope ("exactly the four exits at item 2") is superseded to FIVE. The PAUSED boundary re-scope (v1.91 item 4 / v1.44 §1) is untouched: branch-failure → PAUSED remains scan-free, witnessed at ML5 + FL8.

7. **ORCHESTRATOR_WORKERS follow-on registered: `B-18-FENCE-LEDGER-FIDELITY-OW`.** The pre-build review grounded (check 7): O-W SHARES the zero-footprint ABORT-exit shape (`orchestrator-workers-effect-fence-aborted` fires before its scan), but symmetric inclusion is NOT mechanical — O-W's obligation-4 scan is an inline CASCADE_CANCEL-only loop (its deadline and pause-tier terminal exits never received the M2 scan at all; v1.91 item 2 was explicitly PARALLELIZATION-only), O-W carries a third disposition class (`paused_child_dispositions`), and O-W has its own recovered dict. The honest O-W scope = the aborted-return bypass + the never-landed M2 terminal exits + the union arm against O-W's three-class arms. Registered in the arc-ledger (this PR) with that scope; deliberately NOT silently widened into this arc.

**New witnesses** (`harness-cp/tests/test_workflow_driver_parallelization_warmup.py`, B-18-FENCE-LEDGER-FIDELITY section; names finalized at build):

| # | Pins |
|---|---|
| FL1 (+FL2, FL7 folded) | ABORT exit under warm-up on a resume round: FAILED `parallelization-effect-fence-aborted` unchanged; ABORTED branch → ledger `completed` terminal-ONLY, no step entry, NO store capture (FL7: the aborted arm wins over the recovered-fence arm); withheld recovered peer → ledger `completed`, NO store capture (FL2); `steps_executed` equals branches actually run |
| FL3 | PAUSE deadline-strike FAILED on a resume round: recovered-withheld peer → `completed` not `cancelled`, store untouched; plain withheld sibling → `cancelled` |
| FL3b | Same finding at the CASCADE_CANCEL post-barrier exit (persona-tier-change resume reach) |
| FL4 | This-round INERT re-paused peer at the ABORT exit: inherited arm — ledger `completed` + store capture (the item-4 deliberate addition pinned) |
| FL5 | Negative control: first-round warm-up strike, no fence history → plain `cancelled` only (baseline byte-preserved) |
| FL6 | Negative control: ABORT_BRANCH ordinal records exactly ONE ledger terminal (scoped-abort block's; the scan cannot double-record an ordinal excluded from `branch_plan`) |
| FL8 | Containment: resume-round branch-failure → PAUSED stays scan-free for a recovered fence peer; the new snapshot's `effect_fence_paused_branches` composed from this-round dispositions only |

**Invariants preserved.** NO §5.2 IS-hash change (ledger terminal Literal unchanged: `cancelled`/`completed`/`timed_out`). NO new contract / ADR / fail-class / CXA edge / snapshot schema change. Dispatch markers byte-unchanged; store captures byte-unchanged except the item-4 named addition. `workflow.step_count` unaffected (terminal-only entries). Gate=False + non-fence + first-round paths byte-identical (ML1-ML7 + FL5 green unmodified). Runtime spec UNCHANGED.

Suite state at close: recorded at the PR (harness-cp full suite + runtime non-e2e green; workspace pyright 0/0/0; ruff clean).

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-3C-PREWARM-TIMEOUT-LEDGER` | M2 terminal-exit audit completeness | CLOSED (v1.91) |
| `B-18-FENCE-LEDGER-FIDELITY` | Fence-state × terminal-exit audit records (v1.91 item 6a/6b) | **CLOSED (this arc)** |
| `B-18-FENCE-LEDGER-FIDELITY-OW` | O-W aborted-return bypass + never-landed M2 terminal exits + union arm (three-class arms) | **Registered (this arc, item 7)** |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition | Registered, open (dedicated session) |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_92.md` (delta over v1.91) |
| Arc | B-18-FENCE-LEDGER-FIDELITY — fence-state × terminal-exit audit records (v1.91 item 6 discharge) |
| Committed source | §25.15.2 obligations 3/4/7 (v1.32); v1.65 §1 (ABORT run-level terminal; fence-paused `completed` MUST-NOT-`cancelled`); v1.73 §1 + v1.74 §1 (the abort-family recording split); v1.91 items 3/5/6; `.harness/b18-fence-ledger-fidelity-design-decision-record.md` |
| Disposition | Scan at FIVE terminal exits; aborted arm = ledger `completed` terminal-only capture-less; fence union arm with recovered-withheld = `completed` capture-less; ONE named crash-visible addition (item 4) |
| Decorrelated review | Fable-5 pre-build adversarial design review (advisor unavailable + Codex TLS-blocked in bg session, standing fallback per `[[fable5-fallback-reviewer]]`): VERDICT AMEND, 0 blocking / 3 concern / 3 cosmetic — all folded into the DDR pre-build (byte-identical claim scoped; four-exits correction + FL3b; FL8; steps_executed; wording; cite strengthening; O-W follow-on scope). Post-build decorrelated diff review recorded at the clearance marker. |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED. |
| Runtime spec | UNCHANGED |
| Follow-on status | B-18-FENCE-LEDGER-FIDELITY CLOSED; B-18-FENCE-LEDGER-FIDELITY-OW registered (item 7); B-18-EPOCH-PARTITION remains open (dedicated session) |
