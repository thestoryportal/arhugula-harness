---
artifact: design-substrate/Spec_Control_Plane_v1_58.md
version: v1.58
cleared_at: 2026-06-24T21:30:00-06:00
clearance_type: Phase-7-absorbed-via-impl-to-cleared-spec
back_reference:
  - design-substrate/Spec_Control_Plane_v1_56.md §2 + §3 (the EXPLICIT-PAUSE synthesis fail-closed this lifts + the B-FANOUT-PAUSE-SYNTHESIS registration)
  - design-substrate/Spec_Control_Plane_v1_32.md §25.15.1 (the cleared `pause → PAUSED` contract — the barrier halts BEFORE the post-join synthesis, so the synthesis never ran) + §3/§4 synthesis "fresh first-and-only dispatch" guarantee
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — the design-fork validation (carrier change necessary; `str | None` step_id-only sufficient; effect-free/fresh-dispatch reasoning holds); the ONE-helper material-diff (covers added/removed/changed, including the silent-DROP "removed" case a placement-nested check would miss); the HIERARCHICAL child-level GATE (trace the child re-entry empirically before relaxing the guard — confirmed `execute_workflow(pause_snapshot_input=...)` hits the same entry guard → entry-side option-B covers it, no follow-on needed); the byte-compat both-carriers requirement (PeerFanOut had no drop)
  - the §25.15 / §3-§4 probe (the pause synthesis never ran → identity-only, not replay → impl-to-cleared-spec, no council)
  - out-of-family Codex — diff review, rounds 1-3 caught FOUR findings (3×[P1] + 1×[P2]), all fixed + witnessed: (a) [P1] the hash byte-compat drop was top-level only → a nested HIERARCHICAL `paused_child_branches` child carrier emitted `synthesis_step_id: null` → broke pre-existing nested-snapshot hashes → fixed with a recursive strip; (b) [P1] a synthesis-bearing snapshot resumed under a MISMATCHED fan-out topology (matching synthesis `step_id`) would run the whole fan-out FRESH (the blanket reject incidentally failed closed) → fixed by reading the STRATEGY's expected carrier in the material-diff (a carrier mismatch now surfaces as a fail-closed diff); (c) [P1] round 2 — the same mismatch with the resumed body ALSO dropping the synthesis false-passes the identity diff (both sides None) → fixed with a dedicated `post-join-synthesis-resume-carrier-mismatch` guard; (d) [P2] round 3 — the recursive strip walked EVERY dict incl. recovered-output payloads → a user-data key named `synthesis_step_id` would be silently stripped/uncovered → fixed by making the strip PATH-AWARE (carrier's own field + the known nested-child carrier path only, never recovered output). The pre-existing NON-synthesis carrier/topology mismatch is unchanged (out of arc scope) but now REGISTERED as the forward arc `B-FANOUT-RESUME-CARRIER-TOPOLOGY-MISMATCH`
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.58`

v1.58 is an **impl-to-cleared-spec** delta over v1.57 — the build of `B-FANOUT-PAUSE-SYNTHESIS`, making a synthesis-bearing fan-out EXPLICIT-PAUSE resumable and LIFTING the v1.56 §2 fail-closed (`post-join-synthesis-on-resume-unsupported` on the pause path).

- **§1 — synthesis identity on the pause carrier + material-diff + fresh-dispatch.** The pause carriers (`FanOutResumeState` / `PeerFanOutResumeState`) now record the terminal synthesis's `step_id` (`synthesis_step_id`). On resume the driver material-diffs the re-supplied synthesis identity (presence + `step_id`) against the captured one BEFORE any dispatch: match → recover/re-dispatch branches + FRESH-dispatch the synthesis post-barrier (it never ran on a pause → effect-free, first-and-only); mismatch (added / removed / changed) → fail closed (`post-join-synthesis-resume-material-diff`). A SINGLE helper covers all three divergences, including the silent-DROP "removed" case.
- **§2 — byte-compat.** `synthesis_step_id` is additive default-None; the snapshot hash DROPS it when None (mirrors the `paused_child_branches` drop on FanOut; ADDS the analogous drop to PeerFanOut, which had none) → every existing snapshot hashes byte-identically.
- **HIERARCHICAL child levels** re-enter via `execute_workflow(pause_snapshot_input=child_snapshot)` → the same entry guard, against the child's own snapshot. No separate child mechanism (advisor-gated, traced empirically: `sub_agent_dispatch.py:637` → `child_workflow_runner` → `execute_workflow`).

## Caveats for Phase 7 consumers

- impl-to-cleared-spec: NO new contract / enum / committed-invariant change; an additive carrier field is not an enum/cardinality surface. CP-only (no runtime / store change — on a pause the synthesis never ran, so the v1.56 `EngineOutputStore` synthesis API is not involved).
- The touched hash is the C-CP-26 snapshot-integrity hash, byte-preserved for existing snapshots via the drop-when-None — NOT the §5.2 IS state-ledger hash (unchanged).
- New CP-side free-form fail-class `post-join-synthesis-resume-material-diff` REPLACES the v1.56 §2 `post-join-synthesis-on-resume-unsupported` on the pause path. No closed-enum / cardinality change.
- `step_id`-only material-diff is sufficient (consistent with the branch material-diff; the synthesis is fresh-dispatched not replayed, so a same-`step_id` body change yields a valid fresh synthesis).
- Three registered fan-out crash-resume follow-ons remain (TIMEOUT-REPLAY + PAUSE-RECONSTRUCT + STRICT-TIER-INCOMPLETE) → R-FS-1 stays ACTIVE.

## Notes

- Phase 7 consumers may rely on v1.58 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
