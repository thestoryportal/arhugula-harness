# F1-01 Governance-Substrate Propagation Note — §1.5 → §14.5.1 Citation Correction

## §1 Status block

| Field | Value |
|---|---|
| Artifact | `Governance_Substrate_Propagation_Note_F1-01.md` |
| Type | Citation-correction propagation note (governance-substrate; advisory per `Adversarial_Review_6_iter4.md` F1-01 Resolution path) |
| Status | **Filed** — propagation record |
| Date | 2026-05-14 |
| Authoring discipline | Workflow v1.7 §2.3.3.1 clause (iii) citation-anchor substrate-verification; Workflow v1.7 §7 fidelity-grammar |
| Origin | F1-01 (Class 2 after operator-deferred Reading 1 selection) from `Adversarial_Review_6_iter4.md`; revision-cycle session Segment 3 governance-substrate propagation per session-open OD-3 confirmation ("governance-substrate propagation in same session") |
| Authoritative resolution | OD plan v2.3 §0.8 row 2 ✅ CLOSED + §0.1 Pattern P2 scope-statement extended (filed at Segment 2) |
| Predecessor artifacts (advisory propagation targets) | `P6-CK_Iteration_4_Entry_Handoff.md`; `P6-CK_Iteration_4_Session_Prompt.md` |
| Successor artifact | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Segment 3 close artifact) |

---

## §2 Defect summary

Per `Adversarial_Review_6_iter4.md` F1-01 evidence:

> The cited section "OD spec v1.3 §1.5" does not resolve in `Spec_Operational_Discipline_v1_3.md`. Hash-chain integrity composition is at OD spec v1.3 §14.5.1 (lines 165–178). … Same citation propagated to Entry Handoff §5 row 4 + Session Prompt §3.1 row 4 (3 sites total).

The defect is parsimoniously a typo (dropped "14." prefix from `§14.5.1` yielding `§1.5`) reproduced at three sites during F2-12 cascade-close artifact authoring on 2026-05-14. The Class 1 → Class 2 reclassification at adversarial review per operator-selected Reading 1 is grounded in the typo reading rather than cross-artifact name drift to ADR-D6 v1.2 §1.5 (which is the distinct dedup algorithm contract, not the hash-chain extension).

---

## §3 Citation correction inventory

| # | Site | v2.2-era citation (defective) | Corrected citation | Disposition status |
|---|---|---|---|---|
| 1 | `Implementation_Plan_Operational_Discipline_v2_2.md` §0.8 row 2 (Concern column) | "OD spec v1.3 §1.5 hash-chain integrity composition (extension to ledger_entries schema)" | "OD spec v1.3 §14.5.1 hash-chain integrity composition (extension to ledger_entries schema)" | ✅ CLOSED at OD plan v2.3 §0.8 row 2 (Segment 2 filing 2026-05-14); also substantively absorbed at U-OD-20 acceptance #15 per F2-04 absorption |
| 2 | `P6-CK_Iteration_4_Entry_Handoff.md` §5 row 4 (Concern column) | "OD spec v1.3 §1.5 hash-chain integrity composition extension to ledger_entries schema (plan-side absorption gap)" | "OD spec v1.3 §14.5.1 hash-chain integrity composition extension to ledger_entries schema (plan-side absorption gap)" | **Advisory correction recorded at this note (governance-substrate; outside impl-plan revision boundary per F1-01 Resolution path)** |
| 3 | `P6-CK_Iteration_4_Session_Prompt.md` §3.1 row 4 (parallel row inherited from Entry Handoff §5 row 4) | "OD spec v1.3 §1.5 hash-chain integrity composition extension to ledger_entries schema (plan-side absorption gap)" | "OD spec v1.3 §14.5.1 hash-chain integrity composition extension to ledger_entries schema (plan-side absorption gap)" | **Advisory correction recorded at this note (governance-substrate; outside impl-plan revision boundary per F1-01 Resolution path)** |

---

## §4 Propagation discipline rationale

### §4.1 Why advisory and not full-revision

Per `Adversarial_Review_6_iter4.md` F1-01 Resolution path: "Path A within-artifact revision at OD plan v2.2 §0.8 row 2 citation; §0.1 self-audit scope-statement extension to cover non-§14.5.x citations; **propagation revisions advisable at Entry Handoff + Session Prompt (governance-substrate; outside impl-plan revision boundary)**."

The phrase "outside impl-plan revision boundary" is the discriminator. The OD plan is the canonical artifact for the substantive concern (the hash-chain integrity composition absorption); the Entry Handoff and Session Prompt are governance-substrate artifacts whose rows reference the same concern with citation drift. Re-filing the Entry Handoff and Session Prompt as v1.1 / v1.1 artifacts would be over-engineering for a citation typo correction whose substantive disposition is already canonically recorded at OD plan v2.3 §0.8 row 2 (✅ CLOSED) + §0.1 Pattern P2 scope-statement extension (filed at Segment 2).

The advisory propagation note (this artifact) is the proportionate response: it records the correction at the governance-substrate sites so future readers tracing the §1.5 citation arrive at the canonical §14.5.1 resolution without ambiguity, without requiring re-filing of the predecessor artifacts.

### §4.2 Pattern P2 self-audit scope-statement extension (cross-reference)

The OD plan v2.3 §0.1 (Segment 2 filing 2026-05-14) extended the Pattern P2 self-audit scope-statement to cover ALL "per OD spec v1.3 §X.Y" citations + ALL "per ADR-D{N} v1.{N} §X.Y" citations + ALL "per `Spec_Information_Substrate_v1.md` §X.Y" cross-axis citations across the OD plan body (not only F2-12-cascade-scoped §14.5.x sub-sections as at v2.2). This scope-statement extension is the canonical Pattern P2 prevention surface at OD plan layer; the governance-substrate sites at Entry Handoff §5 row 4 + Session Prompt §3.1 row 4 inherit the corrected citation by reference to this note.

Future revision-cycle session prompts authored from the Entry Handoff + Session Prompt templates should incorporate the corrected citation at first authoring; the cascade-kickoff drafting precedent (advisory observation logged at `Adversarial_Review_6_iter4.md` Cross-artifact pattern surfacing) does not meet the SKILL §6 ≥3-artifact threshold for Workflow §7 session-prompt-template revision, so no template revision is mandated here.

---

## §5 Verification at propagation note close

| Verification | Result |
|---|---|
| OD spec v1.3 contains §14.5.1 with hash-chain integrity composition formula at lines 165–178 | ✅ Verified at OD plan v2.3 Segment 2 substrate read |
| OD spec v1.3 does NOT contain a §1.5 top-level section | ✅ Verified per F1-01 evidence (grep result) |
| OD plan v2.3 §0.8 row 2 cites §14.5.1 (not §1.5) | ✅ Verified at OD plan v2.3 Segment 2 filing |
| OD plan v2.3 U-OD-20 acceptance #15 cites §14.5.1 + lines 165–178 | ✅ Verified at OD plan v2.3 Segment 2 filing per F2-04 absorption |
| Entry Handoff + Session Prompt rows hold the §1.5 typo at original filing 2026-05-14 | ✅ Verified per F1-01 evidence + substrate inspection |
| Advisory correction recorded at this note for the two governance-substrate sites | ✅ This artifact |

---

*End of F1-01 Governance-Substrate Propagation Note. Filed at P6-CK Iter 4 revision-cycle Segment 3. Companion to `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Segment 3 close artifact).*
