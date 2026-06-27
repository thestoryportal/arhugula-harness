---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.90
cleared_at: 2026-06-27T20:00:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the wrong-site-probe correction; the conjunct-1∩{ESR,WAL} decomposition; the 3-link composition argument; the at-most-once scoping [committed-effect non-re-fire vs the separate PROCEED-RESIDUAL arc]; the Codex-before-the-at-most-once-prose gating)
  - by-execution witnesses (the typed predicate verdict flip [fan-out {ESR,WAL}→True RED-without-fix + fan-out {SAVE_POINT,RECONCILER}→False carrier-segregation control]; the CP↔runtime agreement [fan-out-esr True / fan-out-save-point False / nested-fanout-esr True / nested-fanout-save-point False]; the fan-out child crash-resume reconstruction + committed effect-bearing branch non-re-fire; the linear-sequential seed topology fold)
  - out-of-family Codex on the diff (`just codex-review` --base, 2 genuine cross-topology at-most-once [P1] rounds, converged round 3)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.90`

v1.90 records the RUNTIME half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD` — the case-(a) [the child is itself FAN-OUT] slice (paired with CP spec v1.83 → v1.84). The typed mirror predicate `subagent_child_recoverable` (`sub_agent_dispatch.py`) has its topology conjunct 2 relaxed from `SINGLE_THREADED_LINEAR`-only to `LINEAR ∪ (fan-out ∩ {ESR,WAL})`; the agreement witness enforces CP↔runtime parity, and the shared `payload_child_recoverable` handles nested grandchildren (one source of truth).

What was reviewed: a re-dispatched fan-out {ESR,WAL} child reconstructs its aggregate at the `_crash_fan_out_resume` site (the B-FANOUT-OUTPUT-REPLAY branch store) — NOT the LINEAR `reconstruct_final_state` seed the v1.89 case-(a) note wrong-site-probed. No new seed surface (the fan-out child reuses the #774/#777 worker/orchestrator seed); the only new runtime code is the predicate relax + the linear-sequential seed topology fold. A SAVE_POINT/RECONCILER fan-out child has no fan-out replay store ({ESR,WAL} carrier segregation) → fail closed → registered follow-on.

Cross-topology at-most-once fold (out-of-family Codex, 2 [P1] rounds): admitting the same engine ({ESR,WAL}) under both LINEAR and fan-out opened a swap hole (LINEAR-ESR → fan-out, same identity → wrong substrate → run fresh → double-fire). The runtime `_linear_step_disambiguator` (the #786 LINEAR-inline-loop seed surface — no maybe-ran dual gate, self-defends via the seed) folds `topology_pattern` into the seed alongside `step_id` + `engine_class`; the symmetric CP dual-gate marker fold lands at CP v1.84.

Invariants: NO new contract / fail-class / §5.2-hash change (seed-gating + the linear-seed disambiguator are non-attested / per-run transient) / `StepDispatcher` Protocol widening / CXA edge. at-most-once PRESERVED (committed branches auto-resumed, not re-fired; the in-flight-branch disposition is the existing B-FANOUT-CRASH-RESUME-MAYBE-RAN family — no new window; the PROCEED in-flight-effect-bearing re-fire window is the separately-registered operator-gated `…-ORCHESTRATOR-PROCEED-RESIDUAL` arc). CP spec C-CP-25 §25.15 v1.83 → v1.84 is the paired primary contract. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
