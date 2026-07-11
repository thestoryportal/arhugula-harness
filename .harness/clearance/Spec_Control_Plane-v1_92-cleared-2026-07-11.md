---
artifact: design-substrate/Spec_Control_Plane_v1_92.md
version: v1.92
cleared_at: 2026-07-11T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/b18-fence-ledger-fidelity-design-decision-record.md (pre-build DDR, review-folded)
  - Spec_Control_Plane_v1_91.md item 6 (the registered charter this arc discharges)
  - B-18-FENCE-LEDGER-FIDELITY (arc-ledger)
merge_commit: pending (marker rides the bundled-absorption PR)
reviewer_chain:
  - Fable-5 adversarial pre-build DESIGN review (fresh agent; advisor unavailable + Codex TLS-blocked in bg session — standing fallback ladder per [[fable5-fallback-reviewer]]) — VERDICT AMEND, 0 blocking / 3 concern / 3 cosmetic; every DDR cite independently re-grounded at HEAD; both refutation campaigns failed (Q1 consumers verified inert — snapshot-only resume skip-set, store-only crash gate, step-count drain predicate, ML7-safe key collision; Q2 shielding/first-round/PROCEED-unreachability verified); capture-NOT verified load-bearing at the crash-gate code (a completed capture would flip `_crash_pause_trigger` and resurrect a crashed ABORT round as resumable PAUSED); all findings folded into the DDR pre-build (byte-identical claim scoped to the capture-less arms; four-exits correction + FL3b; FL8 containment witness; steps_executed; wording; cite strengthening; O-W follow-on scope per check-7 grounding)
  - Reviewer confirmations (refutation attempts that failed) — ledger `completed` is the committed abort/fence-family dispatch-boundary value (v1.65 §1 fence-paused MUST-NOT-`cancelled`; v1.73 §1 ABORT_BRANCH `completed` for a never-re-dispatched peer; obligation-4 `completed` ⟹ "effect may have landed" = the ambiguous-uncommitted reserve state); obligation-3 step entries target LANDED effects (three committed no-step-entry precedents); operator-resume skip-set reads the snapshot only (store captures feed crash-resume classification alone)
  - impl witnesses (7 new FL tests — FL1(+FL2/FL7 folded)/FL3/FL3b/FL4/FL5/FL6/FL8; harness-cp full suite 1509 green; runtime non-e2e 2360 green; axes 1590 green; workspace pyright 0/0/0; ruff clean; determinism 8/8 on the FL selection)
  - Fable-5 post-build decorrelated DIFF review (fresh agent, main...HEAD, independent suite re-run: 1509 green reproduced, pyright 0/0/0, ruff clean) — VERDICT 0 BLOCKING / 2 CONCERN / 1 COSMETIC; all 8 attack points otherwise CLEAN (DDR fidelity incl. arm-order edge cases with aborted ⊆ recovered noted as ratified belt-and-braces; regression surface; double-record; new-call-site drain verified REAL — branch_writers created at plan time drain regardless of task execution, FL1 the end-to-end witness and fails-on-main; test non-vacuity + helper backward-compat verified against `git show main:`; spec-delta truth; types; cross-spec drift confined to the findings). CONCERN 1 (the scan's own header comment still said "four terminal exits" — the stale-carry class) fixed in-arc → "five". CONCERN 2 (spec item 7 claimed the -OW registration "in this PR" while the diff carried no arc-ledger edit) fixed in-arc → `B-18-FENCE-LEDGER-FIDELITY-OW` row + snapshot bump (registered 2→3) added on the branch, making the sentence true. COSMETIC (CASCADE_CANCEL call-site comment named only the this-round completed variant) fixed in-arc.
---

# Clearance — `Spec_Control_Plane_v1_92.md`

This delta closes **B-18-FENCE-LEDGER-FIDELITY** — the two fence-family audit-fidelity findings registered at v1.91 item 6 from the #928 post-build review. The obligation-4 scan now runs at **five** terminal PARALLELIZATION exits (the fence-ABORT exit added) with a dedicated **aborted arm** (ledger `completed` terminal-ONLY — no step entry, no store capture; `cancelled` foreclosed by obligation-4, the abort semantics carried by the unchanged run-level `fail_class` + the durable fence claim), and the fence arm consults the **union** of this-round and snapshot-recovered fence peers (a recovered-withheld peer records `completed` capture-less instead of the store-contradicting `cancelled`).

**The load-bearing clearance facts.** (1) The v1.91 open semantic question — store-capture-or-not for a cross-attempt fence peer — is answered **CAPTURE-NOT** by the snapshot-carried asymmetry: the still-journaled prior snapshot already carries the peer, so capture-less preserves its fence-recoverable MAYBE-RAN crash classification and reserve resolvability byte-exact; both independent reviews verified at the crash-gate code that a capture would flip `_crash_pause_trigger` and destroy resolvability. (2) The ONE deliberate crash-visible addition is named, not silent: a this-round INERT re-paused peer at the new exit inherits the v1.91 fence-arm capture (the committed v1.65 §1(c) reproduce-the-terminal trade extended to one more exit; FL4-pinned). (3) The O-W counterpart is **registered, not silently widened** (`B-18-FENCE-LEDGER-FIDELITY-OW`; different scan shape + never-landed M2 exits + third disposition class).

## Notes

- NO §5.2 IS-hash change (ledger terminal Literal unchanged); NO new contract/enum/fail-class/CXA edge/snapshot schema; runtime spec UNCHANGED; `workflow.step_count` unaffected (terminal-only synthesis; FL1 pins STEP_BOUNDARY = 0).
- Baseline byte-preserved: first-round / non-fence paths identical (empty recovered dict; FL5 + ML1-ML7 green unmodified); PAUSED boundary stays scan-free (ML5 + FL8).
- Remaining open B-18 follow-ons: `B-18-FENCE-LEDGER-FIDELITY-OW` + `B-18-EPOCH-PARTITION` (both dedicated sessions).
