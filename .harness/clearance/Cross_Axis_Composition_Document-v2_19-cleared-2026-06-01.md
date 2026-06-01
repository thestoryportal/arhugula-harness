---
artifact: design-substrate/Cross_Axis_Composition_Document_v2_19.md
version: v2.19
cleared_at: 2026-06-01T12:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - operator AskUserQuestion 2026-06-01 (R-CXA-4 disposition → "Also probe the v2.18 §2.4 defect"; probe-and-patch-if-confirmed)
  - .harness/clearance/Cross_Axis_Composition_Document-v2_18-cleared-2026-05-31.md (the version this patch corrects)
  - design-substrate/Cross_Axis_Composition_Document_v2_3.md §2.1 + §2.3.4 + §2.4 (canonical OD→IS=4 / matrix since 2026-05-17)
  - design-substrate/Implementation_Plan_Operational_Discipline_v2_11.md §0 (OD-plan-side placeholder resolution, Form A, 2026-05-16)
merge_commit: (pending)
reviewer_chain:
  - pre-substantive empirical grounding (R-CXA-4 probe) — falsified the "stale placeholder cleanup" premise; surfaced the v2.18 matrix defect
  - Explore subagent anchor-resolution sweep (all 11 OD→AS/OD→CP placeholders confirmed resolved to real units at v2.3/v2.11)
  - advisor pass 2026-06-01 (confirmed the 107 cell-sum + precise harm characterization; cautioned against spiraling into the logged 13-vs-11 / 26-vs-27 carries)
  - operator AskUserQuestion 2026-06-01 ratification (probe-and-patch)
  - design-phase posture session 2026-06-01 (operator-declared per workspace CLAUDE.md §11.3)
supersedes: Cross_Axis_Composition_Document-v2_18-cleared-2026-05-31.md
---

# Clearance — `Cross_Axis_Composition_Document v2.19`

v2.19 is a fidelity-pure citation/count-correction patch closing a confirmed defect in v2.18. v2.18 re-absorbed the C3-15 OD→IS cleanup that was **already completed at v2.3** (a wrong-version-read of the v2.1 baseline), corrupting the §2.1 aggregate matrix across three cells and publishing an erroneous aggregate. v2.19 restores the canonical §2.1 matrix (AS→IS **13 → 11**, CP→OD **0 → 8**, OD→CP **8 → 12**; OD→IS **4** unchanged — it was already correct), corrects the aggregate **105 → 107**, and restores the genuine/convention/phase-2 sub-split to **37 / 48 / 22 = 107** (the "37/48/20" at workspace CLAUDE.md §1.1 was a downstream fabrication to make 105 add up). v2.18's OD→IS=4 / OD-outbound=26 end-state was already correct since v2.3 and is preserved — only the §2.1 matrix cells, the aggregate, and the downstream sub-split carried harm.

The "CXA-OD-IS-EDGE-DRIFT" v2.18 claimed to close (halt-doc Item 11) was a phantom drift: CXA's canonical reading (v2.3, 2026-05-17) was already conformed to the OD plan (OD→IS = 4 at §2.3.4 + §2.1 matrix + §2.4); the apparent divergence existed only against the superseded v2.1 baseline. No fork doc filed — fidelity-pure count-correction with conclusive empirical posture follows workspace precedent (OD spec v1.15; CP spec v1.14); operator authorized probe-and-patch at AskUserQuestion 2026-06-01.

This arc also corrects the R-CXA-4 framing at the roadmap/register/dashboard process-substrate layer (Finding A): the OD→AS/OD→CP `U-AS-NN`/`U-CP-NN` placeholders the R-CXA-4 "convention-formalization revision" follow-on targeted were resolved at CXA v2.3 + OD plan v2.11 — the follow-on is a phantom and is withdrawn. R-CXA-4's correct "0 wireable / stays PARTIAL" conclusion is preserved. ZERO production-code change; ZERO contract change; ZERO edge-semantics change; ZERO change to §2.3.x row tables or §3.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed. The canonical §2.1 matrix = v2.16 full matrix + v2.17 CP→IS amendment + v2.3-canonical OD→IS=4; aggregate **107**; genuine **37**; convention **48**; phase-2-runtime **22**.
- Supersedes the v2.18 clearance marker for the §2.1 matrix + aggregate + §2.4 AS-row surfaces only; v2.18's §2.3.4 row content (OD→IS = 4) remains canonical (it was never wrong).
- Pre-existing logged carries left untouched per advisor (the AS-plan-13-vs-CXA-11 divergence; the OD 26-vs-27 cost-attribution overlay).
- See `.harness/clearance/README.md` for marker discipline.
