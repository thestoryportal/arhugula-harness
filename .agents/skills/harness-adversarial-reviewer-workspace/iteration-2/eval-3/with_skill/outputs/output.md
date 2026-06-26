# Adversarial Review — Phase 7 Class 1 Tension Record 002 (TopologyPattern Enum Divergence)

## Summary
- Mode: Phase-7 pre-implementation review — stress-test of a filed `Phase_7_Class_N_Tension` record's finding classification
- Artifact reviewed: `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md`
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: Class 3: 1 · Class 2: 2 · Class 1: 1
- Highest-severity finding: F3-01 — the record omits its §4.1 review-severity classification entirely and conflates the §2.7.6 fork label with a §4.1 class label
- Disposition recommendation: The record's **§2.7.6 fork classification (Class 1 — halt-execution) holds and is correct**. But the record has classification defects of its own — it never states a §4.1 review-severity class, and §2 contains a citation error. Revise the record (current-phase fix); the underlying halt decision and the recommended resolution direction stand.

**Verdict in one line:** The *substance* of Tension 002 — a genuine, non-determinate spec↔plan divergence that must halt U-CP-22 — holds up under verification. The *finding classification* as written does not: it conflates the two Class taxonomies the workspace `CLAUDE.md` and this skill explicitly tell reviewers to keep separate, and it never assigns the §4.1 severity class at all.

---

## Verification performed (primary-source reads)

Every set claimed in the record was read against its cited source:

- **Set 1** (`SINGLE_AGENT, SEQUENTIAL_HANDOFF, PARENT_FANOUT_AGGREGATE, RECONCILER_MESH, ROUTER_DELEGATE, PIPELINE_STAGES`) — verified verbatim against `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 `Signatures` block (line ~1184). v2.2 and v2.3 both declare U-CP-22 "preserved verbatim from v2.1," so the v2.1 body is canonical for v2.3. Confirmed.
- **Set 2** (`single-threaded-linear, orchestrator-workers, decentralized-handoff, hierarchical-delegation, evaluator-optimizer, parallelization`) — verified verbatim against `Spec_Control_Plane_v1_2.md` §10.1 taxonomy table (`Spec_Control_Plane_v1_3.md` §10 declares C-CP-10 "preserved verbatim from v1.2," so v1.2 §10.1 is canonical for v1.3). Confirmed.
- **Set 3** (`ORCHESTRATOR_WORKERS, DECENTRALIZED_HANDOFF, EVALUATOR_OPTIMIZER, PARALLELIZATION, ROUTING, SEQUENTIAL_PIPELINE`) — verified verbatim against root `CLAUDE.md` §5 (line 230), `harness-cp/CLAUDE.md` §4.2 CP-AL-1 (line 168), and `Phase_7_Meta_Architecture_v1.md` §7.4 CP-AL-1 (line 530). `Sub_Agent_Boundary_Specification_v1.md` §5.1 not separately confirmed but the three confirmed copies are byte-identical. Confirmed.
- **Authority chain:** `Spec_Control_Plane_v1_2.md` §10.1 cites ADR-D4 v1.1 §1.1. Read `ADR-D4.md` §Decision item 1 + §1.1 table directly: ADR-D4 v1.1 §1.1 uses Set-2 vocabulary verbatim (single-threaded linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization). ADR-D4 is at v1.1; no later version exists in `design-substrate/` or `design-substrate/archive/`. The record's §4 tiebreaker check resolves: **no later ADR-D4 exists, so the resolution does not invert** — Set 2 is authority-chain-canonical, exactly as the record reasons.

**Conclusion of verification:** Every factual claim in §2 about *what the three sets contain* is accurate. The divergence is real, it is three-way, and Set 1 genuinely shares no member with Set 2 or Set 3. The record did not fabricate the tension.

---

## Class 3 findings (severe — phase re-opening)

### F3-01 — The record omits its §4.1 review-severity classification and conflates it with the §2.7.6 fork label
- **Location:** `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md` title ("Class 1 Spec Tension Record 002"), §1 Detection-state table ("Tension class | **Class 1** (halt-execution ...)"), §3 heading ("Why Class 1 (halt-execution)").
- **Defect:** The record uses a single "Class 1" label throughout. That label is the `Project_Workflow_v1_8.md` §2.7.6 *Phase-7 execution fork* class (Class 1 = halt-execution). The workspace `CLAUDE.md` §4.3 and the `harness-adversarial-reviewer` skill both state explicitly that two distinct Class 1/2/3 taxonomies exist and must not be conflated: the §2.7.6 fork scale (1=halt-execution) and the §4.1 review-severity scale (1=Minor drift, 2=Moderate current-phase revision, 3=Severe phase re-opening). Under the §4.1 scale, this finding is a Phase-6 plan defect whose resolution requires revising a Phase-5 artifact (the spec) — discriminator (b) fires — making it **§4.1 Class 3 (severe — phase re-opening)**. The record names a "Class 1" without ever stating which taxonomy, and the only Class label it gives (1) is the *opposite end* of the §4.1 severity scale from where this finding actually sits. A reader scanning "Class 1 Spec Tension Record" against the §4.1 scale would read this as a minor drift finding. It is not.
- **Discriminator that classifies as Class 3:** (b) — resolving the finding requires revising the spec (`Spec_Control_Plane_v1_2.md`/`v1_3.md` §10.1, a Phase-5 artifact) and ADR-anchored vocabulary, upstream of the Phase-6 plan where the unit lives. Under §4.1 this is Class 3.
- **Evidence:** Title line "Class 1 Spec Tension Record 002"; §1 row "Tension class | **Class 1** (halt-execution ...)". No §4.1 severity class appears anywhere in the document. The skill's own title-section disambiguation: "never let a §4.1 Class-3 finding read as a §2.7.6 Class-3 (informational) fork or vice versa."
- **Anti-fabrication attack engaged:** None (this is a classification-discipline defect, not a fabrication).
- **Axis-domain attack engaged:** CP — enum divergence from spec (the finding the record is *about* is a correct CP-domain catch; the defect here is in how the record labels its own severity).
- **Decision-claim label:** *decided* — the text supports a single reading: the record gives one Class label, it is the §2.7.6 label, and the §4.1 class is absent. There is no second reading.
- **Resolution path:** Revise the record to state both classifications explicitly and separately — the §2.7.6 fork class (Class 1, halt-execution) *and* the §4.1 review-severity class — and label each with its taxonomy. This is a current-phase fix to the record itself; it does not change the halt decision. (Note the §4.1 Class-3 designation describes the *finding's* severity; it does not imply Phase 5 must literally re-open as a full phase — the in-CLI fix regime per the record's own header handles the spec edit. But the §4.1 class must still be stated, per skill discipline.)

---

## Class 2 findings (moderate — current-phase revision)

### F2-01 — §2 misattributes the admissibility-matrix spec citation (§10.3 vs §10.2)
- **Location:** §2 final paragraph: "Spec C-CP-10 §10.3 gives a different admissibility set ..."; §4 step 2: "acceptance #3 (admissibility matrix → align to spec §10.3)".
- **Defect:** The record says U-CP-22's admissibility matrix should align to spec **§10.3**. But U-CP-22 acceptance #3 (verified in `Implementation_Plan_Control_Plane_v2_1.md`) cites "**§10.2** admissibility matrix," not §10.3. Acceptance #2 (CascadePolicy) is the criterion that cites §10.3. Separately, the plan's section-number citations are themselves crossed relative to the spec: in `Spec_Control_Plane_v1_2.md`, §10.2 is "Workflow-definition surface declaration" and §10.3 is "Cross-pattern admissibility per workload class." So the *content* the record describes (admissibility per workload class) does live at spec §10.3 — but the record then tells the operator the plan's acceptance #3 cites §10.3, which it does not. The record's resolution step 2 would instruct an editor to "align acceptance #3 to §10.3" when acceptance #3's own text points at §10.2. This is a citation defect that would propagate into the fix if applied as written.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of the record (the resolution instructions); resolving it requires revising the record's §2 and §4 text. Does not require upstream-artifact revision, so not Class 3.
- **Evidence:** `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 acceptance #3: "`is_admissible` returns `true` per **§10.2** admissibility matrix"; acceptance #2: "`CascadePolicy` declares exactly three values per C-CP-10 **§10.3** verbatim." `Spec_Control_Plane_v1_2.md` §10.2 heading "Workflow-definition surface declaration"; §10.3 heading "Cross-pattern admissibility per workload class."
- **Decision-claim label:** *decided* — the citations in both artifacts are unambiguous on read; the record's claim is straightforwardly wrong on which section acceptance #3 cites.
- **Resolution path:** Correct §2 and §4 to cite the plan's acceptance criteria by the section numbers the plan's own text uses, and to surface that the plan↔spec section-number mapping for §10.2/§10.3 is itself crossed. The fix should disambiguate which spec section carries the admissibility content rather than asserting a single number.

### F2-02 — The record under-scopes the divergence: a second enum in the same unit (CascadePolicy) also diverges, unmentioned
- **Location:** Record §2 ("Defect") scopes the tension to `TopologyPattern` only. U-CP-22 also declares `CascadePolicy`.
- **Defect:** U-CP-22's `Signatures` block declares `enum CascadePolicy { COMPLETE_ALL, CANCEL_ON_FIRST_FAIL, PAUSE_ON_FIRST_FAIL }`, and acceptance #2 requires it "per C-CP-10 §10.3 verbatim." But ADR-D4 §Context and §1.2, ADR-D5 §1.3.1, and spec C-CP-10's `TopologyDeclaration` all commit `cascade_policy ∈ {pause, proceed, cascade-cancel}`. The plan's `CascadePolicy` values are a *third vocabulary* for a *second enum* in the very unit under halt — and the plan's own acceptance #2 ("§10.3 verbatim") cannot be satisfied, the same defect shape as acceptance #1. The record's §2 treats the tension as single-enum; it is at least two-enum. An operator resolving only `TopologyPattern` would land U-CP-22 with `CascadePolicy` still non-verbatim and acceptance #2 still unsatisfiable. This is silent scope narrowing (Attack A2) within the record.
- **Discriminator that classifies as Class 2:** (a) — affects the substantive content of the record (its Defect and Resolution scope). The underlying CascadePolicy divergence, if separately filed, would itself be §4.1 Class 3 by discriminator (b); but the *finding against the record* — that it under-scoped — is a current-phase revision of the record, Class 2.
- **Evidence:** `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 `Signatures` (`CascadePolicy` with `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL`) and acceptance #2. `ADR-D4.md` §Context: "D5 §1.3.1 declared `cascade_policy ∈ {pause, proceed, cascade-cancel}`." `Spec_Control_Plane_v1_2.md` §10.2 `TopologyDeclaration`: `cascade_policy : "pause" | "proceed" | "cascade-cancel"`.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing) — applied to the record itself.
- **Decision-claim label:** *decided* — the second divergence is plainly present in U-CP-22's signature block and is the same unsatisfiable-acceptance shape; this is not reading-dependent.
- **Resolution path:** Broaden the record's §2 Defect and §4 Resolution to enumerate the `CascadePolicy` divergence alongside `TopologyPattern`, so a single operator decision dispositions both enums U-CP-22 declares rather than leaving one to resurface at landing time.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — §3 overstates the CP-AL-1 / Set-3 coupling
- **Location:** §3: "CP-AL-1 (which embeds Set 3) ... so any change to the canonical enum touches a load-bearing anti-leakage rule."
- **Defect:** Set 3 appears in CP-AL-1, but CP-AL-1 is an *anti-leakage rule* — its function is to assert that H_E sub-agent topology ≠ H_T's TopologyPattern enum. CP-AL-1's enum list is illustrative of "the 6 H_T pattern values" for the inequality; it is not a value-contract the harness materializes. The record's phrasing ("any change ... touches a load-bearing anti-leakage rule") is true but reads as if the enum *itself* is load-bearing at the H_E↔H_T boundary, when what is load-bearing is the *inequality assertion*, which survives any consistent renaming. This does not change the resolution (Set 3 still needs reconciliation to Set 2 for consistency) — it is a precision drift in how §3 motivates the Class designation.
- **Discriminator:** (a/b/c) all miss — this is prose precision, not a content or upstream-revision defect.
- **Evidence:** `Phase_7_Meta_Architecture_v1.md` §7.4 CP-AL-1 statement and "Anti-pattern foreclosed" column; `harness-cp/CLAUDE.md` line 176 "CP-AL-1 is the most load-bearing rule at the H_E ↔ H_T boundary" — load-bearing-ness attaches to the *rule*, not the enum spelling.
- **Resolution:** Inline clarification in §3 that what CP-AL-1 makes load-bearing is the H_E≠H_T inequality, and that the Set-3 reconciliation is a consistency fix so the illustrative enum stays aligned with the canonical one — not a change to the anti-leakage rule's force.

---

## Findings considered and rejected (transparency)

- **Attack A4 (fabricated citations).** Spot-checked every set against its cited source (plan v2.1 U-CP-22, spec v1.2 §10.1/§10.2/§10.3, ADR-D4 §1.1, root + harness-cp `CLAUDE.md`, Meta-Architecture §7.4). All three sets resolve verbatim. The record fabricated nothing. No finding.
- **Authority-chain reasoning (record §4).** Verified: spec §10.1 → ADR-D4 v1.1 §1.1, and ADR-D4 §1.1 uses Set-2 vocabulary. The record's conclusion that Set 2 is authority-chain-canonical is correct and correctly grounded in `CLAUDE.md` §1.3. No finding.
- **§4 tiebreaker check.** The record asks the operator to confirm no later ADR-D4 exists. Verified directly: ADR-D4 is at v1.1, no later version in `design-substrate/` or `archive/`. The tiebreaker resolves in favor of the record's recommendation; the resolution does not invert. The record was correct to flag it as an operator check rather than asserting it. No finding.
- **Is the halt itself warranted? (§2.7.6 fork-class check).** U-CP-22 acceptance #1 demands the enum "per C-CP-10 §10.1 verbatim" while the plan's own signature is not verbatim from §10.1 — the unit's acceptance criterion is literally unsatisfiable as written, and choosing the canonical vocabulary is a non-determinate design-authority decision. That is exactly the §2.7.6 Class-1 (halt-execution) trigger. The fork classification is **correct**. No finding against the fork class.
- **Attack A8 (framing contamination).** Checked whether the record overcommits a stack/persona/deployment value or picks a five-axis architectural decision outside the ADR path. It does not — it explicitly defers the canonical-enum selection to the operator and routes through the authority chain. No finding.
- **FM-C (author-mode drift) in the record.** The record's §4 is labeled "Proposed resolution (operator decision required)" and §5 states "This record does not apply any fix." It correctly stops at recommending a direction. No author-mode finding against the record.
- **Sibling assessment (§6).** Spot-checked U-CP-15: signature `EngineClass { EVENT_SOURCED_REPLAY, SAVE_POINT_CHECKPOINT, PURE_PATTERN_NO_ENGINE, RECONCILER_LOOP, WAL_SEGMENT }` matches C-CP-07 §7.1 five-element taxonomy. The §6 claim that U-CP-15 is clean and independently implementable holds on the enum check. U-OD-01/U-OD-04 not separately verified (out of the CP corpus scope of this review) — flagged as unverified, not as a finding.
- **Axis-domain mechanical-application check (FM-D).** Did not treat "enum divergence" as automatically a record-level finding; verified the divergence's outcome appears in the artifacts (it does) and confined record-level findings to genuine defects in the record's own reasoning/scope/citation.

---

## Disposition

**The finding classification in Tension Record 002 partially holds.**

What holds:
- The **§2.7.6 Phase-7 fork classification — Class 1 (halt-execution)** — is correct and verified. U-CP-22's acceptance #1 is unsatisfiable as written; the resolution requires a non-determinate design-authority choice; halting U-CP-22 before code lands is the right call.
- The factual content of §2 (the three sets) is accurate and verbatim-verified.
- The §4 authority-chain reasoning and Set-2 recommendation are sound; the tiebreaker resolves in the recommendation's favor.

What does not hold:
- **F3-01 (Class 3 under §4.1):** The record never states its `Project_Workflow_v1_8.md` §4.1 review-severity class and uses the bare label "Class 1" — which, read against the §4.1 scale, points to *minor drift*, the opposite of this finding's actual §4.1 severity (Class 3, discriminator (b): plan defect requiring spec revision). The workspace `CLAUDE.md` §4.3 and the reviewer skill both prohibit exactly this conflation. The record must state both Class taxonomies explicitly and label each.
- **F2-01 (Class 2):** §2/§4 misattribute the admissibility-matrix citation — acceptance #3 cites spec §10.2, not §10.3; the plan↔spec §10.2/§10.3 mapping is itself crossed. Applying the fix as written would propagate the wrong section number.
- **F2-02 (Class 2):** The record under-scopes the tension. `CascadePolicy` — a second enum in the same unit — also diverges (`COMPLETE_ALL/CANCEL_ON_FIRST_FAIL/PAUSE_ON_FIRST_FAIL` vs ADR/spec `{pause, proceed, cascade-cancel}`) with the same unsatisfiable-acceptance defect at acceptance #2. A `TopologyPattern`-only resolution leaves U-CP-22 still un-landable.
- **F1-01 (Class 1):** §3 slightly overstates the CP-AL-1/enum coupling.

**Recommended action:** Keep the halt — do not lift it. Revise the tension record before the operator dispositions it: (1) add an explicit §4.1 review-severity class (Class 3) stated separately from the §2.7.6 fork class (Class 1), each labeled with its taxonomy; (2) correct the §10.2/§10.3 citation in §2 and §4; (3) widen §2/§4 scope to cover the `CascadePolicy` divergence so one operator decision dispositions both enums. None of these change the resolution *direction* (adopt Set 2) — they make the record safe to execute the fix against. Per the record's own header (in-CLI fix regime, back-flow deprecated 2026-05-15), the spec/plan/CLAUDE.md edits are applied in-CLI once the operator confirms; this review does not author those edits.
