# Cross-Axis Composition Document (v2.19)

*Delta over v2.18. v2.19 is a **fidelity-pure citation/count-correction patch** (no contract change, no edge-semantics change, no new design) closing a confirmed defect introduced at v2.18: v2.18 **re-absorbed the C3-15 OD→IS cleanup that was already completed at v2.3** (a wrong-version-read of the v2.1 baseline), corrupting the §2.1 aggregate matrix across three cells and publishing an erroneous aggregate count. v2.19 restores the canonical §2.1 matrix (AS→IS **13 → 11**, CP→OD **0 → 8**, OD→CP **8 → 12**; OD→IS **4** unchanged), corrects the aggregate **105 → 107**, and restores the genuine/convention/phase-2 sub-split to **37 / 48 / 22 = 107**. The v2.18 §2.3.4 (OD→IS → 4) and §2.4 (OD outbound → 26) **values were already correct** since v2.3 — those v2.18 claims were redundant restatements that happened to land on the right numbers; only the §2.1 matrix cells + aggregate carry harm. The "CXA-OD-IS-EDGE-DRIFT" v2.18 claimed to close (halt-doc Item 11) was a **phantom drift**: the CXA canonical reading was already conformed to the OD plan at v2.3 (OD→IS = 4 at §2.3.4 + §2.1 matrix + §2.4 since 2026-05-17); the apparent divergence existed only against the superseded v2.1 baseline. ZERO change to §2.3.1 / §2.3.2 / §2.3.3 / §2.3.4 / §2.3.5 / §2.3.6 / §2.3.7 / §2.2 row tables (v2.3-canonical, preserved verbatim). Downstream propagation of the erroneous 105 (workspace `CLAUDE.md` §1.1 + dashboard) corrected in the same arc. Operator-authorized at AskUserQuestion 2026-06-01 (probe-and-patch-if-confirmed). 2026-06-01.*

## §0 Change note (v2.18 → v2.19)

### §0.1 Revision context — v2.18 erroneous-delta closure (R-CXA-4 probe finding)

This arc opened as the operator-picked **R-CXA-4** "CXA convention-formalization cleanup" (delete/remap the stale OD→AS/OD→CP `U-AS-NN`/`U-CP-NN` placeholder rows, framed at register §B-14 + dashboard as "mirroring v2.18's C3-15 OD→IS cleanup"). Pre-substantive empirical grounding **falsified the task premise** and, in doing so, surfaced a deeper defect in v2.18 itself.

Two findings:

**Finding A — R-CXA-4 is a phantom task (the `U-AS-NN`/`U-CP-NN` placeholders were resolved ~2 weeks ago).** The OD→AS (§2.3.5) and OD→CP (§2.3.6) placeholder rows the R-CXA-4 follow-on targets were **resolved to their real producer unit IDs at CXA v2.3** (2026-05-17), with C/G/R class labels added — e.g. `U-OD-17 → U-AS-14`, `U-OD-29 → U-AS-15` (G), `U-OD-23 → U-CP-46`, `U-OD-21 → U-CP-09`. The mirror resolution landed at **OD plan v2.11** (2026-05-16, "Form A citation-precision delta"; resolution table `.harness/cxa_7c_placeholder_resolution.md`). The `#### §2.3.5 OD → AS` / `§2.3.6 OD → CP` full row-table headers appear only in v2.1 / v2.2 / v2.3 — **v2.3 is canonical HEAD**; every v2.4–v2.18 delta states "§2.3.5 / §2.3.6 preserved verbatim." There is **no stale-placeholder cleanup to do at either CXA or the OD plan.** The R-CXA-4 register/dashboard framing read the **v2.1 baseline** (pre-resolution) and concluded "stale placeholders, convention-formalization revision owed" — a wrong-version-read mis-framing (workspace `CLAUDE.md` §10.5). R-CXA-4's *substantive* conclusion ("0 wireable edges; stays PARTIAL") is correct and matches v2.3's classification; only its named follow-on task is the phantom.

**Finding B — v2.18 is an erroneous delta built on the same wrong-version-read.** v2.18 §0.4 claims "§2.1 matrix at OD→IS cell: **6 canonical** (v2.1 baseline preserved verbatim through v2.17)" and amends "OD→IS 6 → 4 / aggregate 107 → 105." But OD→IS has been **4** at every canonical site since v2.3 (§2.3.4 = 4 rows; §2.1 matrix cell = 4 per v2.3 line 113; §2.4 OD = 4+10+12 = 26), and every v2.4–v2.17 delta states "ZERO change to §2.3.4." The two U-OD-27 rows v2.18 "deleted" (sqlite substrate + ring-buffer eviction) were already struck as part of v2.3's "10 spurious struck." v2.18 therefore **double-subtracted an already-absorbed cleanup** and, in re-rendering the §2.1 matrix from the v2.1 baseline, corrupted three additional cells.

This v2.19 patch closes Finding B (the substantive design-substrate defect) and records Finding A (the R-CXA-4 framing correction is applied at the roadmap/register/dashboard process-substrate layer in the same PR).

### §0.2 Sections corrected

§0 (this change note); §2.1 (aggregate 4×4 matrix — three corrupted cells restored + aggregate 105 → 107 + sub-split 37/48/20 → 37/48/22); §2.4 (per-axis posture — AS outbound 13 → 11 + aggregate 105 → 107; OD row + cost-attribution overlay convention preserved verbatim). All §2.3.x per-bucket row tables PRESERVED VERBATIM (v2.3-canonical; v2.18 did not touch them — only the §0.4 narrative + §2.1 matrix were wrong). §3 (Pattern P1) PRESERVED VERBATIM.

### §0.3 §2.1 aggregate matrix correction

**v2.18 published (corrupted):**

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 13 ✗ | *(self)* | 0 | 0 |
| **CP** | 43 | 19 | *(self)* | 0 ✗ |
| **OD** | 4 | 10 | 8 ✗ | *(self)* |

v2.18's cells sum to **97**, yet it declared **105**, and the correct value is **107** — three independent inconsistencies. Root cause: v2.18 rebuilt the matrix from the v2.1 baseline (`AS→IS = 13`, `CP→OD = 0`), bolted on the post-baseline annotated cells (`CP→IS 43`, `CP→AS 19`, `OD→IS 4`), and mis-placed the `CP→OD = 8` value (v2.9) into the `OD→CP` cell — losing the v2.3 reclassification of `AS→IS` (13 → 11), `CP→OD`, and `OD→CP`.

**v2.19 canonical (restored = v2.16 full matrix + v2.17 CP→IS amendment):**

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | **11** | *(self)* | 0 | 0 |
| **CP** | **43** *(v2.17)* | **19** *(v2.15)* | *(self)* | **8** *(v2.9)* |
| **OD** | **4** *(v2.3)* | 10 | 12 | *(self)* |

Cell sum: AS→IS 11 + CP→IS 43 + CP→AS 19 + CP→OD 8 + OD→IS 4 + OD→AS 10 + OD→CP 12 = **107**.

### §0.4 Aggregate + sub-split correction

**Aggregate: 105 → 107.** The correct HEAD aggregate is v2.17's **107**, which v2.18 should never have changed (the OD→IS bucket was already 4 at v2.17). 

**Sub-split: 37 genuine + 48 convention + 22 phase-2-runtime = 107.** v2.18 did **not** restate the genuine/convention/phase-2 sub-counts in its file; the "37 / 48 / **20** = 105" split that appears at workspace `CLAUDE.md` §1.1 is a **downstream fabrication** derived to make v2.18's wrong 105 add up (the −2 was attributed to phase-2-runtime). The canonical sub-split is v2.17's unchanged **37 / 48 / 22 = 107**.

### §0.5 §2.4 per-axis attribution correction

v2.18 §2.4 corrupted the **AS outbound** value to **13** (should be **11** — matrix-consistent; the v2.16/v2.17 §2.4 canonical) and carried the aggregate **105** (should be **107**). v2.19 restores AS = 11 and aggregate = 107.

**Preserved verbatim (NOT touched by v2.19 — separate logged carries):**
- The **OD 26 / overlay-27** attribution-divergence convention (v2.9 §0.3: the cost-attribution `cost.*` seam lives in the CP→OD bucket at §2.1 but is attributed to OD outbound at §2.4; the §2.1 OD-row sum reads 26, the §2.4 attribution overlay reads 27). Both representations net to 107.
- The **AS-plan-13-vs-CXA-11** divergence (AS plan v1.2 §3.4 declares 13 AS→IS edges; CXA canonical = 11 since v2.3 per the 2-spurious strike). v2.19 restoring AS = 11 is **fixing v2.18's corruption**, not re-litigating this carry — CXA canonical was always 11; the carry (plan 13 vs CXA 11) is unaffected and remains logged at v2.17 §0.7(iii).

### §0.6 Root cause — wrong-version-read of a delta-only baseline

The CXA chain is delta-only: the canonical table is the **last full re-table plus subsequent cell-amendments**, never the v2.1 baseline. v2.18 (and, independently, the R-CXA-4 grounding at PR #222) read the **v2.1 baseline** for the OD buckets — where the placeholders are still present and OD→IS = 6 — instead of the v2.3-canonical reading (placeholders resolved; OD→IS = 4). The same disease produced both Finding A and Finding B. The reusable rule: **in a delta-only artifact chain, never read the baseline as canonical — read the last full re-table + applied cell-amendments.**

### §0.7 Harm characterization (precise)

| v2.18 claim | Disposition |
|---|---|
| §2.3.4 OD→IS → 4 rows | **Redundant, but correct** (already 4 since v2.3). No harm; no v2.19 change. |
| §2.4 OD outbound → 26 | **Redundant, but correct** (already 26 since v2.3). No harm; no v2.19 change. |
| §2.1 matrix AS→IS = 13 | **HARM** — should be 11. Corrected. |
| §2.1 matrix CP→OD = 0 | **HARM** — should be 8. Corrected. |
| §2.1 matrix OD→CP = 8 | **HARM** — should be 12. Corrected. |
| aggregate 105 | **HARM** — should be 107. Corrected. |
| sub-split 37/48/20 (downstream) | **HARM** — should be 37/48/22. Corrected. |
| "closes CXA-OD-IS-EDGE-DRIFT (halt-doc Item 11)" | **Phantom drift** — CXA was already conformed at v2.3; no real drift existed at canonical reading. |

This is **not** "the whole v2.18 delta reverted" — the OD→IS = 4 / OD outbound = 26 end-state v2.18 asserted is correct and is preserved. Only the §2.1 matrix cells, the aggregate, and the downstream sub-split carry actual harm.

### §0.8 Downstream propagation corrected (same arc)

(a) Workspace `CLAUDE.md` §1.1 CXA row: `105 canonical` → `107`; `37/48/20` → `37/48/22`; the "aggregate 107→105 at v2.18 … workspace-derived pending CXA-side restatement" framing → v2.19 correction. ✅ this PR.

(b) Workspace `CLAUDE.md` §2.4 CXA row: v2.18 → v2.19 bump with this change-note. ✅ this PR.

(c) `.harness/roadmap_status.md` dashboard + `Project_Roadmap_v1.md` §5 + `.harness/post-phase-8-forward-register.md` §B-14: R-CXA-4 framing correction (Finding A — placeholders resolved at CXA v2.3 + OD plan v2.11; the "convention-formalization revision owed" follow-on is a phantom). ✅ this PR.

(d) `harness-od/CLAUDE.md` carries the **correct** 4 / 26 counts (no aggregate-105 cite); its "divergence closed at v2.18" framing is a harmless historical phantom-drift artifact, but the values are right. **Left untouched** (no count error to fix; not spiraled into per the advisor's scope discipline; a per-axis CLAUDE.md is a Phase-7-posture surface). Noted here for completeness.

(e) The prior **PR #128 "R-IF-HYGIENE-CXA-COUNT-CASCADE"** propagated the erroneous 105 into "canonical pointers"; v2.19 + (a)–(d) reverse that cascade to 107.

### §0.9 R-CXA-4 disposition (Finding A)

R-CXA-4 ("OD multi-seam") remains **PARTIAL** with the **correct** substantive conclusion preserved: 0 wireable edges (the 1 genuine OD→IS data-flow seam is already wired; the 6 phase-2-runtime edges are already materialized at bootstrap stage 6; the convention edges are discharged by §3 Pattern P1 + stage-6 `verify_*`). The phantom follow-on ("CXA convention-formalization revision to delete/remap stale `U-AS-NN`/`U-CP-NN` placeholders") is **withdrawn** — those placeholders were resolved at CXA v2.3 + OD plan v2.11. No design-substrate cleanup is owed for R-CXA-4.

### §0.10 Clearance marker

Per workspace `CLAUDE.md` §4.5: clearance marker filed at `.harness/clearance/Cross_Axis_Composition_Document-v2_19-cleared-2026-06-01.md`.

---

## §1 — Cross-arc note

v2.19 is a fidelity-pure citation/count-correction patch in the workspace's established precedent (OD spec v1.15 phantom-as-described closure; CP spec v1.14 cite-correction). It corrects a confirmed arithmetic/matrix defect in a merged + operator-ratified + cleared predecessor (v2.18, PR #110 `2f14604`). No fork doc is filed — fidelity-pure count-correction with conclusive empirical posture follows that precedent; the operator authorized the probe-and-patch at AskUserQuestion 2026-06-01, and the finding is grounded byte-exact against the v2.3 / v2.16 / v2.17 canonical tables. The advisor pass (2026-06-01) confirmed the 107 cell-sum and the harm characterization.

The "halt-doc Item 11 CXA-OD-IS-EDGE-DRIFT" that v2.18 claimed to close was a **phantom** — CXA's canonical reading (v2.3) was already conformed to the OD plan. v2.18 did no harm to the OD→IS end-state (4 / 26 were already canonical) but corrupted the surrounding §2.1 matrix and aggregate by reading the v2.1 baseline. v2.18's sibling, OD plan v2.27 (halt-doc Item 12, the OD-internal carve-out), is unaffected — it preserved §4.5 verbatim and is independently correct.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_19.md` |
| Filing event | Fidelity-pure correction of v2.18's erroneous §2.1 matrix + aggregate. §2.1 matrix AS→IS 13→11 / CP→OD 0→8 / OD→CP 8→12 (OD→IS 4 unchanged); aggregate 105→107; sub-split 37/48/20→37/48/22. Root cause: wrong-version-read of the v2.1 baseline (v2.18 re-absorbed the C3-15 OD→IS cleanup already done at v2.3). v2.18's OD→IS=4 / OD-outbound=26 end-state was already correct and is preserved. Bundled with the R-CXA-4 framing correction (Finding A) at the roadmap/register/dashboard layer. Operator-authorized at AskUserQuestion 2026-06-01. 2026-06-01 |
| Authored at | Design-phase posture session 2026-06-01 (operator-declared per workspace `CLAUDE.md` §11.3) |
| Authoring authority | Operator AskUserQuestion 2026-06-01 (probe-the-v2.18-§2.4-defect, patch if confirmed) + advisor confirmation of the 107 cell-sum + harm characterization |
| Predecessor | `Cross_Axis_Composition_Document_v2_18.md` (§2.1 matrix + aggregate + §2.4 AS-row corrected; all §2.3.x row tables + §3 preserved verbatim — they were never wrong, only v2.18's §0.4 narrative + §2.1 matrix were) |
| Canonical reading | The canonical §2.1 matrix = the v2.16 full matrix + v2.17's CP→IS 37→43 amendment + the (already-canonical-since-v2.3) OD→IS = 4. Aggregate **107**; genuine **37**; convention **48**; phase-2-runtime **22**. |
| Successor | TBD per next CXA arc |
| Clearance marker | `.harness/clearance/Cross_Axis_Composition_Document-v2_19-cleared-2026-06-01.md` |
