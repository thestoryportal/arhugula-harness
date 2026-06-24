---
artifact: design-substrate/Spec_Control_Plane_v1_59.md
version: v1.59
cleared_at: 2026-06-24T22:30:00-06:00
clearance_type: Phase-7-absorbed-via-impl-to-cleared-spec
back_reference:
  - design-substrate/Spec_Control_Plane_v1_58.md §1 (the synthesis-only carrier/topology-mismatch guard this generalizes + the §1 "non-synthesis … unchanged" carve-out this closes + the registration of B-FANOUT-RESUME-CARRIER-TOPOLOGY-MISMATCH)
  - design-substrate/Spec_Control_Plane_v1_32.md §26.2 (the C-CP-26 never-co-set resume-carrier invariant — a snapshot populates exactly one carrier, read on resume by only its pausing strategy) + §25.15.x (each strategy's recovery reads only its own carrier; `_is_resume = <own carrier> is not None`)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — the design-fork validation: the uniform "populated carrier must match the resuming strategy" rule is BOTH simpler and more correct than a fan-out-only carve-out (a fan-out-only version needs MORE conditional logic); the subsumption is safe because the both-dropped synthesis false-pass keys on carrier-populated not synthesis identity; scope the four strategy-dispatch carriers as the core, gate `effect_fence_resume` on verifying its capture site is linear-only (verified clean — the only fence-pause capture is `workflow_driver.py:3006` inside the linear step loop, never a fan-out strategy function); record the superset (don't silently expand the registered "fan-out" title), don't fragment handoff/EO into separate arcs (no deferred design problem, just one guard); confirm the crash-resume path can't surface a foreign carrier
  - the §26.2 / §25.15.x carrier-invariant probe (the never-co-set + read-own-carrier-only invariants are already cleared → the fail-closed guard is impl-to-cleared-spec, no council)
  - out-of-family Codex — diff review (carrier/topology mismatch is the EXACT class Codex flagged 3× across 2 rounds at B-FANOUT-PAUSE-SYNTHESIS; this arc is the general close)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.59`

v1.59 is an **impl-to-cleared-spec** delta over v1.58 — the build of `B-FANOUT-RESUME-CARRIER-TOPOLOGY-MISMATCH`, generalizing the v1.58 §1 synthesis-only carrier/topology-mismatch guard to ALL topology resume carriers and closing the v1.58 §1 "non-synthesis … unchanged" carve-out.

- **§1 — general resume-carrier/topology consistency guard.** At the explicit pause-resume entry (`resume_snapshot is not None`), BEFORE any dispatch, the driver fails closed (`resume-carrier-topology-mismatch`) when the snapshot's populated topology resume carrier (`fan_out_resume` / `peer_fan_out_resume` / `handoff_resume` / `evaluator_optimizer_resume` / `effect_fence_resume`) is NOT read by the resuming strategy. A topology change between pause and resume would otherwise have the strategy read its absent carrier → run the whole topology FRESH → re-dispatch effect-bearing branches/stages (an at-most-once violation). The guard SUBSUMES the v1.58 synthesis-only `_synthesis_resume_carrier_mismatch` (removed) — it keys on carrier-populated alone, so it covers the synthesis-bearing case + the previously-unguarded non-synthesis fan-out / handoff / evaluator-optimizer / effect-fence carriers. The `post-join-synthesis-resume-material-diff` synthesis identity check is retained and runs after, against a carrier-consistent snapshot.
- **§2 — the v1.58 §1 carve-out is closed** (stale-carry refresh): the "non-synthesis … unchanged" closing parenthetical no longer holds after this arc.

## Caveats for Phase 7 consumers

- impl-to-cleared-spec: NO new contract / enum / committed-invariant change. The guard ENFORCES the existing §26.2 never-co-set carrier invariant + the §25.15.x read-own-carrier-only recovery contract. CP-only (no runtime / store / carrier-schema / hash change — the guard is a read-only consistency check at the resume entry).
- New CP-side free-form fail-class `resume-carrier-topology-mismatch` SUPERSEDES the v1.58 `post-join-synthesis-resume-carrier-mismatch` (now a strict subset). No closed-enum / cardinality change.
- The crash-resume path (`resume_snapshot is None`) reconstructs each strategy's own carrier keyed to the executing topology, so a foreign carrier cannot be surfaced there — the guard is scoped to the explicit pause-resume entry only.
- `effect_fence_resume → SINGLE_THREADED_LINEAR` is safe: a fence-ambiguous pause is only ever captured in the linear/TOOL_STEP step loop (`workflow_driver.py` `_execute_workflow_body`), never a fan-out strategy function.
- Three registered fan-out crash-resume follow-ons remain (TIMEOUT-REPLAY + PAUSE-RECONSTRUCT + STRICT-TIER-INCOMPLETE) → R-FS-1 stays ACTIVE (G1.1 = 3 + 0).

## Notes

- Phase 7 consumers may rely on v1.59 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
