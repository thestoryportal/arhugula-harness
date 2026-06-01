# Adversarial Review — Project_Workflow v1.14 (§7.5 Process-discipline catalogue)

## Summary
- Mode: Phase-7 / design-substrate pre-merge review (§10.9 standing posture A — pre-merge gate). FIRST workflow-doc delta reviewed under this posture.
- Artifact reviewed: `design-substrate/Project_Workflow_v1_14.md` (PR #201)
- Date: 2026-06-01
- Finding count by class: Class 3: 0 · Class 2: 0 · Class 1: 1 (+ 2 process observations)
- Highest-severity finding: F1-01 (incomplete supersession cite-span — drift)
- Disposition recommendation: **CLEAR with one inline Class-1 fix** (§4.1.1) — apply F1-01, then merge. The two process observations are not v1.14-content defects (one is a skill-internal activation tension; one is the already-operator-surfaced must_pass[1] disposition).

---

## Class 3 findings (severe — phase re-opening)

None.

## Class 2 findings (moderate — current-phase revision)

None.

## Class 1 findings (minor — documentation drift)

### F1-01 — PD-4 supersession cite-span undercounts the §7.4.7.2-misframing carry
- **Location:** `Project_Workflow_v1_14.md` §7.5.2 PD-4 row ("SUPERSEDES the U-RT-111 v2.36 §7.4.7.2-sub-species framing") + §3 (a) ("the U-RT-111 runtime-plan v2.36 change-note framed PD-4 as a '§7.4.7.2 sub-species cardinality 1→2'") + the clearance marker's PD-4 supersession paragraph.
- **Defect:** The §7.4.7.2-sub-species framing of `plan-revision-against-not-yet-built-substrate` did not appear only at v2.36 — it was carried forward at each subsequent rescope: v2.36 ("cardinality 1 → 2 at workflow doc §7.4.7.2"), v2.37 ("2 → 3 at workflow doc §7.4.7.2"), v2.38 ("3 → 4 at workflow doc §7.4.7.2"), all empirically present in workspace `CLAUDE.md` §2.4. v1.14 supersedes "the v2.36 framing" but the stale framing spans **v2.36 + v2.37 + v2.38** (three versions). This is the workspace's own multi-version stale-carry shape (cf. workflow §7.4.7 sibling-spec-staleness checklist item 2). The supersession *disposition* is sound (v1.13 §3(a) is the authority and discriminated the pattern NOT-§7.4.7.2-shape — confirmed); only the cite-span is incomplete.
- **Discriminator that classifies as Class 1:** (a/b/c) all miss — this is a cross-reference completeness gap that does not change v1.14's semantics (PD-4 supersedes the framing regardless of how many versions carried it). Drift only.
- **Evidence:** `grep` of `CLAUDE.md` §2.4 returns three "cardinality N → N+1 at workflow doc §7.4.7.2" framings of the pattern (v2.36 / v2.37 / v2.38).
- **Anti-fabrication attack engaged:** A4 (cite-resolution) — the v2.36 cite resolves but is incomplete vs the actual carry span.
- **Resolution path:** Inline fix — broaden the PD-4 supersession cite from "v2.36" to the "v2.36 → v2.38" carry span at the three sites (§7.5.2 PD-4 row, §3 (a), clearance marker). Author applies; the disposition (SUPERSEDED) is unchanged.

---

## Process observations (NOT v1.14-content findings; surfaced for transparency)

### PO-1 — Skill-internal activation tension (meta)
- The skill's §"Activation discipline / Do NOT use" lists "the workflow document, or other meta-substrate" as out-of-scope, while the newer (2026-05-31) §"Standing posture" A extends the pre-merge gate to "any `design-substrate/**` amendment" (and the `R-600-workflow-v1-14-amendment` roadmap entry lists this reviewer as a secondary skill). For the workflow-doc-amendment case these conflict. Resolved in favor of the newer, more-specific standing posture (review performed). **This is a candidate finding against the skill itself** (route to a future skill-revision arc reconciling the exclusion with standing-posture A) — NOT a v1.14 defect. Cardinality 1; logged for observation.

### PO-2 — must_pass[1] disposition unratified (already operator-surfaced)
- The `R-600-workflow-v1-14-amendment` roadmap entry's `must_pass[1]` ("next-action derivation rule canonicalized at workflow doc layer") was marked N/A-as-malformed in the entry's notes. Per the pre-done advisor, that disposition is the operator's call, not a notes-field disposition. Already surfaced explicitly in the PR #201 description ("RESOLVED-pending … must_pass[1] needs operator confirmation"). Not a v1.14-content defect; tracked at the PR layer.

---

## Findings considered and rejected (transparency)

1. **Checklist item 1 (stale-carry-text within v1.14):** v1.14's §2 "preserved verbatim" claims are accurate — it does not edit §7.4/§7.4.7; the self-audit table is fresh. No internal stale carry. ✓ handled.
2. **Checklist item 3 (forward-cite phantom):** all cited unit IDs (U-CORE-01, U-OD-41, U-OD-51, U-RT-86, U-RT-111), PRs (#79/#83/#84/#85, #196), and the `.harness/retirement-event-pattern-catalogue.md` path resolve at HEAD. ✓ verified by grep/ls.
3. **Checklist item 8 (X-AL-3 anti-extension):** §7.5 is workflow-grammar (process discipline), declares ZERO new H_T primitive/contract/axis, ZERO cross-axis cascade. Does not extend H_T design. ✓ — strongest pass; v1.14 explicitly catalogues *existing* disciplines.
4. **§7.5 placement (sibling-to-§7.4 vs §7.4.7.X):** correct — the seeded disciplines are not stale-carry-text disposition (the §7.4.7 domain) nor fidelity-claim grammar (§7.4.1–6); nesting under §7.4.7 would degrade taxonomy coherence per the v1.13 §3(a)/(c) warning. The §7.4↔§7.5 boundary statement is legible. ✓ handled.
5. **§7.5.1 inclusion gate — PD-1 (halt-route-split-AC):** ≥3 independent arcs (U-CORE-01 + U-OD-41 + U-OD-51, distinct units/sessions). Passes all 3 gate conditions. ✓.
6. **§7.5.1 inclusion gate — PD-2 (use-the-product-probe):** ≥4 independent probe arcs (PRs #79/#83/#84/#85). Passes. ✓.
7. **§7.5.1 inclusion gate — PD-3 (verification-shape):** ≥2 independent arcs; partial home at CLAUDE.md §13.1 correctly handled via cite-don't-relocate (gate condition 3). ✓ — §13.1 verified to say "verify by execution, not unit tests."
8. **§7.5.1 inclusion gate — PD-4 (plan-revision-against-not-yet-built):** single-unit-multi-rescope (all U-RT-111) — labelled honestly per §7.5.2 + §3 (d), admitted under the v1.11/v1.13 single-instance-at-first-cataloguing precedent. Not misrepresented as multi-arc-independent. ✓ (cite-span issue is F1-01, separate).
9. **`landed-substrate-pending-upstream` exclusion:** correct — operator-ratified to the `.harness/` retirement-event-pattern catalogue as sub-species 7d; §7.5.1 gate condition 3 (no canonical home elsewhere) excludes it; §7.5.4 documents the cross-catalogue routing. Double-homing would re-litigate. ✓ handled.
10. **Parked-candidate independence gate:** carried-fork-audit (FF-2/FF-3 both OD-7b = 1 arc) + impl-time-grounding (PR #37/#38 same cascade) correctly parked OPEN for failing the independent-arc cardinality condition. ✓ — matches the advisor's independence finding.
11. **External-canon mode (FM-D judgment):** §7.5 is governance meta-substrate, not an axis contract; the research-corpus / axis-domain attacks do not apply. Recorded as inapplicable, not a missed finding.
12. **Severity-inflation self-check (FM-A):** resisted escalating F1-01 to Class 2 — the supersession disposition is semantically unchanged by the cite-span gap; it is genuinely drift-only. Distribution (0/0/1) is sane for a well-grounded delta.

---

## Disposition

**CLEAR with one inline Class-1 fix** per Project_Workflow §4.1.1. Apply F1-01 (broaden the PD-4 supersession cite from v2.36 to the v2.36 → v2.38 carry span at three sites), then merge PR #201. No Class 2 / Class 3 findings → no current-phase revision or phase re-opening owed. PO-1 (skill activation tension) routes to a future skill-revision arc; PO-2 (must_pass[1]) is tracked at the PR for operator confirmation. No §2.7.6 Phase-7 fork results.
