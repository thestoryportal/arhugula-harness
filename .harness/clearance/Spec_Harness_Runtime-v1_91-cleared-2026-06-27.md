---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.91
cleared_at: 2026-06-27T22:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the DECOMPOSE discriminator [SAVE_POINT as the #779 fan-out analogue; RECONCILER grounded separately]; the CAN-vs-DOES capture-producer requirement [by-execution RED-without-fix, not a predicate unit test]; the #788 swap-fold check; the RECONCILER representability tie-breaker)
  - by-execution witnesses (the typed predicate verdict flip [fan-out {ESR,WAL,SAVE_POINT}→True + fan-out RECONCILER→False carrier-segregation control + LINEAR scope unaffected]; the CP↔runtime agreement [fanout-child-save-point True / fanout-child-reconciler False / nested-fanout-save-point-grandchild True / nested-fanout-reconciler-grandchild False]; the RED-without-fix SAVE_POINT fan-out child crash-resume reconstruction + committed effect-bearing branch non-re-fire; the cross-topology signature fold for the new engine)
  - out-of-family Codex on the diff (`just codex-review` --base)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.91`

v1.91 records the RUNTIME half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD-SAVE-POINT` — the SAVE_POINT slice of the `…-FANOUT-CHILD-SAVE-POINT-RECONCILER` follow-on the v1.90 carrier-segregation note registered. The runtime typed mirror `_SUBAGENT_RECOVERABLE_FANOUT_CHILD_ENGINE_CLASSES` (the fan-out-engine leg of `subagent_child_recoverable` conjunct 2, which gates the composer's deterministic `child_run_id_seed`) is widened {ESR,WAL} → {ESR,WAL,SAVE_POINT}, mirroring the CP `_FANOUT_REPLAY_ENGINE_CLASSES` widen (the agreement witness enforces parity). Paired with CP spec change-note v1.84 → v1.85.

Grounding overturn (SAVE_POINT only): the fan-out branch-capture store is the engine-class-AGNOSTIC `EngineOutputStore`; the fan-out aggregate reconstruction `_determine_fanout_resume` consumes ONLY that store, NOT the ESR/WAL-only §8.1 cached-output-replay channel; the §14.22 effect fence is auto-active for SAVE_POINT (`_DURABLE_AUTO_FENCE_ENGINE_CLASSES` includes all four). SAVE_POINT is the §11.2 ABOVE_ENGINE reading — harness branch store is the sole aggregate authority, no engine-owned competing substrate, no CAS/F-1 window. RECONCILER (the §11.2 RECONCILER reading) carries an ungrounded two-authorities + CAS/F-1 question → the registered `…-FANOUT-CHILD-RECONCILER` follow-on (the decompose, mirroring #779→#781).

Cross-topology at-most-once — already covered by the #788 fold (no new hole): the CP `_payload_engine_signature` dual-gate marker already folds `f"{topology}:{engine}"` and the runtime `_linear_step_disambiguator` already folds topology into the seed, so a fan-out SAVE_POINT signature `parallelization:save-point-checkpoint` is distinct from the bare LINEAR-SAVE_POINT marker and every other combo → a LINEAR↔fan-out or fan-out↔fan-out SAVE_POINT swap fails the dual gate closed / re-derives a fresh seed. `{engine_class, topology_pattern}` stays the complete recovery-selecting pair; SAVE_POINT only adds a member to the already-folded engine axis.

Invariants: NO new contract (a constant widen of an existing predicate), NO new fail-class, NO §5.2-hash change (the seed-gating + the linear-seed disambiguator are non-attested / per-run transient), NO `StepDispatcher` Protocol widening, NO new CXA edge. at-most-once PRESERVED (SAVE_POINT fires NO CAS-claim → no F-1 window; the in-flight-branch disposition is the EXISTING B-FANOUT-CRASH-RESUME-MAYBE-RAN family, no new window). CP spec C-CP-25 §25.15 v1.84 → v1.85 is the paired primary contract. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED. No operator gate (additive recovery for a previously-fail-closed surface, no committed-invariant sacrifice).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
