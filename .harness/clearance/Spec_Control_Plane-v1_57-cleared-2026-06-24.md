---
artifact: design-substrate/Spec_Control_Plane_v1_57.md
version: v1.57
cleared_at: 2026-06-24T18:00:00-06:00
clearance_type: Phase-7-absorbed-via-impl-to-cleared-spec
back_reference:
  - .harness/class_1_fork_fanout_crash_resume_cascade_policy.md (the Class-1 finding this arc closes)
  - design-substrate/Spec_Control_Plane_v1_32.md §25.15.1 + §25.15.2 obl. 7 (the cleared cascade contract the recovery implements)
  - design-substrate/Spec_Control_Plane_v1_55.md §2 (the PR1-scoped fail-closed this supersedes)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — the BLOCKING capture-before-cancel verification (the failing branch is captured `completed`-no-output before the `raise` that triggers the cancel; the dichotomy is total), the "not-yet-dispatched ≠ effect-free" correction (cancelled siblings must not re-dispatch), the orchestrator false-negative catch (verified: orchestrator failure is a separate direct-FAILED path, not a cascade trigger), the PAUSE probe-resolution (naive reconstruct spec-foreclosed → fail-closed + sub-arc)
  - the §25.15 probe (obligation 7 + §25.15.1 dictate the semantics → impl-to-cleared-spec, no council)
  - out-of-family Codex — diff review (pending convergence)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.57`

v1.57 is an **impl-to-cleared-spec** delta over v1.56 — the build of `B-FANOUT-CRASH-RESUME-CASCADE-POLICY`, making fan-out crash-resume cascade-policy-AWARE and LIFTING the PR1 (v1.55 §2) blanket fail-closed for PAUSE + CASCADE_CANCEL.

- **§1 — cascade-aware recovery (strict-tier-conservative, Codex [P1] + advisor reconcile).** For the strict tiers a crash-resume CONTINUES only when COMPLETE (every branch recovered → nothing to re-dispatch) ∧ no-error; every other state fails closed. Errored branch → CASCADE_CANCEL reproduce FAILED no-re-dispatch (obligation 7 + §25.15.1) / PAUSE fail-closed-ambiguous. INCOMPLETE recovery → fail closed (`...-incomplete-recovery`): an absent branch is indistinguishable from ran-but-uncaptured (the dispatch-before-capture window; branches are effect-BEARING) — re-dispatch is unsafe → broad recovery is the registered `B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE` follow-on (needs at-most-once branch dispatch). COMPLETE∧no-error → continue (finalize, re-dispatch nothing). PROCEED unchanged (PR1).
- **§2 — PAUSE-trigger stays fail-closed.** Naive reconstruct is spec-foreclosed (§25.15.1 "finish in-flight, then pause" can't be honored from a crash-interrupted store) → the registered `B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT` sub-arc.

## Caveats for Phase 7 consumers

- impl-to-cleared-spec: NO new contract / enum / committed-invariant change; the semantics are dictated by the cleared §25.15.1 + obligation 7. CP-only (no runtime / store change — detection reuses `output is None` + the carrier counts).
- Honest scoping: this slice delivers correct CASCADE_CANCEL→FAILED + complete-recovery completion; the common incomplete-crash recovery for the strict tiers stays fail-closed (the broad lift needs at-most-once branch dispatch — a registered follow-on, NOT named-savior-cited).
- New CP-side free-form fail-classes (`fan-out-crash-resume-cascade-cancel`, `-pause-trigger-ambiguous`, `-cascade-policy-incomplete-recovery`) scope the former `fan-out-crash-resume-cascade-policy-unsupported` blanket to the ambiguous cases. No closed-enum / cardinality change.
- CASCADE_CANCEL FAILED uses store-only audit (the disposition keystone), NOT ledger re-materialization — a deliberate choice (a FAILED run attests no aggregate; obl. 3 met by the store).
- Three registered fan-out crash-resume follow-ons remain (TIMEOUT-REPLAY + PAUSE-RECONSTRUCT + STRICT-TIER-INCOMPLETE) plus B-FANOUT-PAUSE-SYNTHESIS → R-FS-1 stays ACTIVE.

## Notes

- Phase 7 consumers may rely on v1.57 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
