---
artifact: design-substrate/Spec_Control_Plane_v1_60.md
version: v1.60
cleared_at: 2026-06-24T23:15:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Control_Plane_v1_57.md §1 (the cascade-policy-aware crash-resume that lifted the strict-tier fail-closed for COMPLETE recovery only + registered B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE as "broad incomplete recovery … needs at-most-once branch dispatch — reserve-before-dispatch, so an absent branch is provably not-yet-run")
  - design-substrate/Spec_Harness_Runtime_v1.md §14.22 C-RT-31 (the effect-fence `try_reserve` reserve primitive this mirrors at branch granularity) + §14.23 C-RT-32 (the EngineOutputStore carrier the marker/stamp API extends)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.78 (the paired runtime delta — the dispatched-marker + instrumented-stamp sidecar API)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — the design validation + BLOCKING cross-version catch: the marker-as-effect-fence-analogue mechanism + the new-spec-delta (not impl-to-cleared-spec) instinct + no-council/no-operator-gate are all correct; BLOCKING — a PRE-arc crash journal has no markers for ANY branch including a maybe-ran one, so classifying its absent branches "provably not-run" would re-dispatch + double-fire → the per-run dispatch-instrumented stamp guards it (`[[durable-recovery-presence-validity-scope]]`); the marker must be fsynced strictly BEFORE dispatch (THE named invariant); state-3 is "maybe-ran" not "ran-but-uncaptured" (the marker separates provably-not-run from maybe-ran, it does not eliminate ambiguity); verify hierarchical keying + PROCEED-unchanged + hash/envelope-inert; don't over-cite the marker as the savior for TIMEOUT-REPLAY / PAUSE-RECONSTRUCT
  - the §25.15 / §26.2 at-most-once probe (the at-most-once guarantee is preserved + strengthened — re-dispatch only on proof-of-not-fired; impl-with-additive-substrate, no council — no nameable cross-domain tension)
  - out-of-family Codex — diff review (pending at PR-open; the dispatch-before-capture window class is exactly what Codex flagged 3-6× across the prior B-FANOUT arcs)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.60`

v1.60 is a **bundled-absorption** delta over v1.59 (co-published with runtime v1.78 + `harness-cp`/`harness-runtime` impl) — the build of `B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE`, adding a reserve-before-DISPATCH at-most-once primitive that lifts the v1.57 §1 strict-tier incomplete-recovery fail-closed for the COMMON (provably-not-run) case.

- **§1 — reserve-before-dispatch strict-tier incomplete-crash recovery.** A durable per-(run, branch) dispatch marker (C-RT-32 `record_branch_dispatched`), written synchronously + fsynced STRICTLY BEFORE each strict-tier branch dispatches (atomic with the dispatch scheduling — no false-positive marker), so marker-absent ⟺ effect-not-fired. On a strict-tier (PAUSE / CASCADE_CANCEL) crash-resume with an INCOMPLETE recovered set: classify absent branches via `present_dispatched_indexes − recovered` — empty ⟹ every absent branch provably-not-run ⟹ recover captured + re-dispatch only the not-run ones; non-empty ⟹ a maybe-ran branch ⟹ fail closed. Index-scheme-agnostic (set difference, not `range(expected)`).
- **§2 — cross-version dispatch-instrumented stamp.** A per-run stamp (C-RT-32 `record_dispatch_instrumented`) written at fan-out start on the strict tiers; the §1 classification trusts the markers ONLY when the stamp is present (a pre-arc un-stamped journal retains the conservative fail-closed) — the BLOCKING cross-version double-fire guard.
- **§3 — the v1.57 §1 carve-out is partially closed** (stale-carry refresh): "incomplete recovery → fail CLOSED" is now scoped to the maybe-ran subcase + the un-stamped journal.
- **§4 — registers `B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION`** (the maybe-ran fire→capture window resolution, the fan-out analogue of the effect-fence HITL-route family) + **`B-FANOUT-CRASH-RESUME-ORCHESTRATOR-DISPATCH`** (the orchestrator `steps[0]`'s own pre-existing dispatch-before-capture window — this slice covers WORKER/PEER branches only). R-FS-1 stays ACTIVE (G1.1 = 4 + 0).

## Caveats for Phase 7 consumers

- Bundled-absorption: additive at-most-once substrate. NO new contract / enum / committed-invariant change. At-most-once is PRESERVED + strengthened — a branch is re-dispatched ONLY when the marker proves its effect did not fire. §25.12 D1/D1.b + §25.15.1 cascade contract + the C-CP-26 §26.2 PauseSnapshot envelope PRESERVED LITERALLY. No §5.2 IS-hash / §16.5 key change (the markers + stamp are a non-attested recovery sidecar, not in the §6 chain).
- PROCEED is UNCHANGED — it writes no marker and consumes none (its recovery accepts the dispatch-before-capture window per the v1.56 PR2-round-4 precedent).
- The marker keys on the SAME `(run_idempotency_key, branch_index)` as `record_branch`. Cross-level hierarchical segregation is safe by construction: `run_idempotency_key = sha256(run_id, workflow_id)` and each hierarchical level re-enters with a DISTINCT child `workflow_id` → a distinct store dir → no branch_index collision across levels (WITNESSED: `test_crash_resume_hierarchical_top_level_provably_not_run_recovers`).
- Scope: WORKER/PEER branches only. The ORCHESTRATOR_WORKERS `steps[0]` orchestrator's own dispatch-before-capture double-fire window is PRE-EXISTING (accepted since v1.55/v1.57) and NOT closed here — registered as `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-DISPATCH` (§4; the orchestrator is a sequential dispatch, not a fan-out branch).
- The maybe-ran subcase (a dispatch marker with no terminal capture — the fire→capture window) still fails closed; its resolution is the registered `B-FANOUT-CRASH-RESUME-MAYBE-RAN-RESOLUTION` follow-on.
- Four registered fan-out crash-resume follow-ons remain (MAYBE-RAN-RESOLUTION + ORCHESTRATOR-DISPATCH + TIMEOUT-REPLAY + PAUSE-RECONSTRUCT) → R-FS-1 stays ACTIVE (G1.1 = 4 + 0).

## Notes

- Phase 7 consumers may rely on v1.60 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
