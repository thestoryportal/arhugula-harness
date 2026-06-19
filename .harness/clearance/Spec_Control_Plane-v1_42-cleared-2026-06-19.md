---
artifact: design-substrate/Spec_Control_Plane_v1_42.md
version: v1.42
cleared_at: 2026-06-19T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — additive C-CP-26 §26.2 carriers + an additive defaulted PauseSnapshot field; materializes the R-CC-1 design §1.1 self-documented MVP re-open trigger, not a committed-invariant sacrifice)
back_reference:
  - .harness/class_2_fork_b_fanout_pause_resumable_fan_out.md
  - .harness/class_3_fanout_pause_resume_not_yet_materialized.md (interim deviation CLOSED by this arc for ORCHESTRATOR_WORKERS)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-FANOUT-PAUSE spine BUILT note + 4 registered forward arcs)
  - .harness/r-cc-1-arc-3-workflow-durable-resume-design-v1.md (§1.1 + §6 re-open trigger — materialized here for the fan-out case)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — identified piece (b) output-recovery as the real design-fork-first surface (breaks R-CC-1 §1.1's position-only model), drove the gate discriminator (read §1.1 source → self-documented re-open, not a forbidding invariant → adopt-and-note), the hash-coverage requirement, and the scope-grounding for the forward arcs
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.42`

v1.42 is an additive delta over v1.41 absorbing the **R-FS-1 standalone arc `B-FANOUT-PAUSE`** — resumable `cascade_policy=pause` fan-out for `ORCHESTRATOR_WORKERS`. It adds two frozen `extra="forbid"` carriers on **C-CP-26 §26.2** (`FanOutBranchResumeState` / `FanOutResumeState`) + one additive, defaulted field `PauseSnapshot.fan_out_resume: FanOutResumeState | None = None`, and materializes the cleared **§25.15.1 `pause → PAUSED`** row for `ORCHESTRATOR_WORKERS` (closing the interim Class-3 deviation `class_3_fanout_pause_resume_not_yet_materialized.md` for that strategy).

**NO operator gate.** The §25.15.1 `pause → PAUSED` row + §25.15.2 obligation 7 (ledger-based terminal-skip resume) are ALREADY cleared; this arc supplies the missing mechanism. The completed-branch OUTPUT recovery (the ledger carries causality + `terminal_status`, not the dispatch output) materializes the R-CC-1 design §1.1 *re-open trigger* — a descriptive MVP scoping note that **explicitly anticipates** this extension ("a future execution model … would need a state-restoration story + a durable store carrying more than the position-only PauseSnapshot"), NOT an explicit invariant forbidding it (contrast B4-Slice-4's §14.5.3 inv 2 relaxation, which DID gate). So adopt-and-note + clearance under the FULL-SPEC directive.

Reviewed during clearance: the carrier (`FanOutResumeState` in `PauseSnapshot`, COVERED by `snapshot_hash` when present — the resumed aggregate trusts the recovered outputs, so a tamper fails `attempt_resume`'s recompute → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`; the key is added to the canonical hash dict ONLY when non-`None`, so existing snapshots hash byte-identically and still validate); the honest no-false-PAUSED guard (PAUSED only when `pause_resume_protocol` is bound, else FAILED + `pause-resume-protocol-not-bound`); the pause semantic (in-flight finish → terminal; not-yet-dispatched left re-dispatchable — the cascade-cancel obl-4 `cancelled` scan deliberately NOT run on `pause`); the material-diff `worker_count` guard; the scope split (ORCHESTRATOR_WORKERS only; the other 4 non-linear strategies registered as forward arcs — each carries its own `*-pause-resume-not-yet-materialized` FAILED branch).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- The now-false "no working-state rehydration is required" prose in the runtime `api.resume` docstring is refreshed to note the fan-out exception (the linear / single-step resume stays position-only).
- See `.harness/clearance/README.md` for marker discipline.
