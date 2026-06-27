---
artifact: design-substrate/Spec_Control_Plane_v1_84.md
version: v1.84
cleared_at: 2026-06-27T20:00:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the WRONG-SITE-PROBE correction [the v1.83 §24 "genuinely unwired" probed the LINEAR `reconstruct_final_state` seed, correctly unreachable by a fan-out child; a fan-out child reconstructs at the SEPARATE `_crash_fan_out_resume` site]; the conjunct-1∩{ESR,WAL} decomposition that BLOCKS [relaxing topology alone leaves SAVE_POINT/RECONCILER fan-out children with no replay store → fresh restart → at-most-once hole]; the 3-link composition argument [parent re-dispatch topology-agnostic + child reconstruction witnessed + in-flight at-most-once is the existing family]; the at-most-once scoping [committed-effect non-re-fire is the claim; the PROCEED in-flight window is the separate registered PROCEED-RESIDUAL arc]; the gating sequence Codex-BEFORE-the-at-most-once-prose)
  - by-execution witnesses (the fan-out child crash-resume reconstruction over the REAL `compose_child_workflow_runner` → `execute_workflow` [captured branches fire-once, in-flight re-dispatches, aggregate result-faithful] + committed effect-bearing branch non-re-fire; the predicate verdict flip [fan-out {ESR,WAL}→True RED-without-fix + fan-out {SAVE_POINT,RECONCILER}→False carrier-segregation control]; the CP↔runtime agreement; the cross-topology signature fold + the linear-sequential seed topology fold)
  - out-of-family Codex on the diff (`just codex-review` --base, 2 genuine cross-topology at-most-once [P1] rounds — the dual-gate marker `_payload_engine_signature` topology fold, then the linear-sequential seed `_linear_step_disambiguator` topology fold — both fixed with RED-without-fix witnesses; round 3 clean on the arc)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.84`

v1.84 records the CP half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD` — the **case-(a) [the child is itself FAN-OUT]** slice the v1.83 §24 registered (C-CP-25 §25.15). The `_subagent_child_recoverable` predicate's conjunct 2 is relaxed from `SINGLE_THREADED_LINEAR`-only to **`LINEAR ∪ (fan-out ∩ {ESR,WAL})`**. Paired with runtime spec change-note v1.89 → v1.90.

Disposition correction (the load-bearing reversal): the v1.83 §24 "genuinely unwired" rested on a WRONG-SITE probe — it looked at the LINEAR `reconstruct_final_state` seed, which is *correctly* unreachable by a fan-out child (the concurrent strategies early-return before it). A fan-out child reconstructs at the SEPARATE `_crash_fan_out_resume` site (the B-FANOUT-OUTPUT-REPLAY branch store). A by-execution probe at the CORRECT site shows a re-dispatched fan-out {ESR,WAL} child reconstructs result-faithfully under its deterministic child run_id. So the case is the EXISTING fan-out crash-resume machinery applied recursively + a predicate relax — NOT a new mechanism, much lighter than the v1.83 "heavy" framing.

Carrier segregation (the decomposition that blocks): conjunct 1 admits all four durable classes, but the fan-out reconstruction substrate (`_fanout_replay_store` → `_FANOUT_REPLAY_ENGINE_CLASSES = {ESR,WAL}`) is DISTINCT from the LINEAR reconstruction substrate (the class-agnostic `reconstruct_final_state` seed, all four). Relaxing conjunct 2 to admit fan-out while conjunct 1 stays at all four would mark a SAVE_POINT/RECONCILER fan-out child recoverable with NO replay store → fresh restart → an at-most-once hole. The relax therefore INTERSECTS fan-out with {ESR,WAL}; SAVE_POINT/RECONCILER fan-out children stay fail-closed → registered follow-on (`…-FANOUT-CHILD-SAVE-POINT-RECONCILER`; fan-out + {SAVE_POINT,RECONCILER} is representable — no load-time topology×engine validator forbids it; `engine_class` is operator-specified).

Lighter than NONLEAF-CHILD (#786) — no new seed surface. A fan-out child is re-dispatched by the EXISTING #774 worker / #777 orchestrator seed (the outer seam, unchanged); its aggregate reconstructs via the EXISTING B-FANOUT-OUTPUT-REPLAY machinery; its in-flight branches re-dispatch through the EXISTING B-FANOUT-CRASH-RESUME-MAYBE-RAN family at the SAME `execute_workflow`. The only new code is the predicate relax + the two identity-guard topology folds.

The cross-topology at-most-once identity guard (out-of-family Codex, 2 genuine [P1] rounds, converged). The relax admits the SAME engine ({ESR,WAL}) under BOTH LINEAR and fan-out, opening a swap hole: a child dispatched LINEAR-ESR whose resumed manifest swaps ONLY topology to fan-out (same engine/workflow_id/step_id) would reuse the same child run_id against a DIFFERENT recovery substrate → run fresh → double-fire. TWO co-landed folds close it across both protection surfaces: (1) the dual-gate marker `_payload_engine_signature` folds topology in (LINEAR keeps the bare engine value — byte-identical #774..#786 marker; fan-out prepends `topology:`) so ANY topology swap fails the marker==resumed comparison closed; (2) the linear-sequential seed `_linear_step_disambiguator` (the #786 LINEAR-inline-loop path, which carries NO dual gate and self-defends via the seed) folds topology in alongside step_id + engine so a topology swap re-derives a different seed → fresh run_id, not a wrong-substrate auto-resume.

At-most-once scope (the honest claim): the relax introduces NO new at-most-once window versus the LINEAR slice. A fan-out child's in-flight branch re-dispatch is the SAME tier-governed maybe-ran disposition as any fan-out run (the existing B-FANOUT-CRASH-RESUME-MAYBE-RAN family). The witnesses prove committed-effect non-re-fire. The in-flight-effect-bearing-branch-under-PROCEED re-fire window is the SEPARATELY-registered operator-gated `…-ORCHESTRATOR-PROCEED-RESIDUAL` arc, not this one.

Spec-vs-fork: bundled-absorption amendment, NOT X-AL-3. v1.83 §24 explicitly named the fan-out-child case as a registered follow-on (a fail-closed gap, NOT a committed closed predicate). The at-most-once invariant is committed; this delta extends recovery additively to a previously-fail-closed surface using the EXISTING substrate, sacrificing no committed decision → no operator gate (v1.77 §3 precedent). NO §5.2 IS-hash change (the topology signature fold is on the non-attested `child_engine_class` marker; the linear-seed disambiguator is per-run transient); NO new contract / ADR / enum / fail-class / Protocol widening / CXA edge. `closure_gate.py` G1.1 was `2 + 0`; after close 1 + register 1, `standalone_registered` stays `2` (net-zero), `standalone_closed` 65 → 66 → R-FS-1 stays ACTIVE.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
