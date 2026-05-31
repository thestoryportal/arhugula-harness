---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.3
cleared_at: 2026-05-30T23:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md (PR #89; §10 + §11 addenda)
  - PR #89 (apply-pass arc carrying this clearance)
merge_commit: <pending — fills at apply-pass PR merge>
reviewer_chain:
  - systems-architect Mode 3 tension-resolution arc (architect rec body)
  - operator AskUserQuestion 2026-05-30 Q-set ratification (Q1=γ-family + Q1.1=γ + Q2=narrow + Q3=bundled + Q4=inline)
  - apply-pass session D1 AskUserQuestion 2026-05-30 ratification (Q-α=(α-1) content-hash + Q-β=(β-3) direct-compute via single 4-legal-pair AUQ)
  - pre-substantive advisor passes at AUQ design + apply-time empirical orientation × 3 (55th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`)
  - impl-time grounding pass surfacing 3 findings (replay-semantics ambiguity; prompts-referent absent; resolver-residence cycle) per `[[impl-time-grounding-pass-pre-merge-revision]]` precedent — findings 1+2 absorbed pre-commit; finding 3 splits arc into docs-half-landed + impl-half-deferred per arch rec §11
---

# Clearance — `Spec_Information_Substrate v1.3`

Spec v1.3 amends v1.2 with three substantive changes for Phase 7 H_T-IS-2 substitution-retirement preparation: (1) NEW §5.1 D-derivative sidecar field `procedural_tier_snapshot_ref: Identifier | None` extending the F-layer six-field shape per ADR-F2 §Consequences (c) extension authorization; (2) NEW §5.2 resolver contract `resolve_procedural_tier_snapshot(harness_context) -> Identifier` declaring a content-hash recipe (2-component scope at v1.3: skills versions + routing-manifest SHA; prompts component deferred to v1.x runtime-binding-extension arc per spec §5.2 Deferral footer) + direct-compute storage discipline (no separate registry persists; resolver re-computes from current HarnessContext); (3) §C-IS-02 line 170 inline canonical-reading patch reconciling MAY/MUST composition (`action_id` MAY encode action class per §5 footer; procedural-tier traceability MUST flow via the §5.1 sidecar field, not via action_id encoding).

Cleared at apply-pass session 2026-05-30 close. Three structural surprises surfaced at impl-time empirical orientation; findings 1+2 absorbed pre-commit (replay-semantics ambiguity resolved at AUQ design; prompts component deferred at v1.3 per X-AL-3); finding 3 (resolver-residence cycle: `harness-runtime/types.py:88-90` imports from harness-is at runtime, forecloseing the architect-rec-assumed harness-is residence) splits the apply-pass arc into docs-half-LANDED (this spec v1.3 + plan v2.4 + arch rec §11) + impl-half-DEFERRED (Q-γ residence-decision AUQ at next session per arch rec §11.4.1; 3 options enumerated with empirical-viability gate for (γ-3) Protocol pattern).

**H_T-IS-2 transit posture caveat for Phase 7 consumers:** spec v1.3 lands the contract-shape substrate at IS-axis (sidecar field + resolver contract); H_T-IS-2 remains **STILL-BOUNDED** at session close per X-AL-2 second conjunct (substituted H_E surface not yet retired at substitution site — no resolver impl + no EntryPayload sidecar field landing + no producer-site lifts). PARTIAL transit owed at follow-on impl arc once Q-γ residence ratified. RETIRED transit owed at full producer-site lift across ~13 sites per per-axis cascade follow-on arcs (deferred per Q2=narrow).

## Notes

- Spec change-notes appended at top of `Spec_Information_Substrate_v1.md` per delta-only single-file convention; v1 + v1.1 + v1.2 sections preserved verbatim.
- §[coherence pass] preservation discipline preserved per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.2 — v1.3 is a Phase 7 substantive amendment arc, not a P5-CK clearance arc; coherence-audit re-run not required per workspace `CLAUDE.md` §11.4 mixed-posture default.
- Co-published: `Implementation_Plan_Information_Substrate_v2_4.md` (NEW delta file absorbing spec v1.3 amendments at U-IS-11 sidecar field + NEW U-IS-18 resolver primitive unit).
- ZERO cross-axis cascade at this arc per Q2=narrow ratification (CP / runtime / AS specs + plans unchanged; CXA unchanged; ADR / ADD / PRD unchanged).
- Sub-species catalogue candidate at workflow v1.13 §7.4.7.2: `[[architect-rec-assumed-cross-package-binding-fails-impl-time-empirical-orientation]]` — first instance; awaits second for sub-species addition.
