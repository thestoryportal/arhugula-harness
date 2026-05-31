---
artifact: design-substrate/Cross_Axis_Composition_Document_v2_18.md
version: v2.18
cleared_at: 2026-05-31T12:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/halt-overnight-expansion-2026-05-31.md (Halt-2 — Item 11)
  - design-substrate/Implementation_Plan_Operational_Discipline_v2_4.md §0.4.2 (C3-15 Path (i-refined) operator ratification, Session 3)
  - design-substrate/Implementation_Plan_Operational_Discipline_v2_4.md §6 Filing-footer adjacent finding (CXA-OD-IS-EDGE-DRIFT logged 2026-04-XX)
  - operator AskUserQuestion 2026-05-31 Option (A) CXA-conforms-to-plan ratification
merge_commit: (pending)
reviewer_chain:
  - probe-first empirical orientation at v2.18 arc (PR #94 standing-posture amendment 5)
  - council deliberation discriminated-out at nameable-tension check (PR #94 amendment 1) — no real voice-tension; C3-15 ratification already operator-decided
  - operator AskUserQuestion 2026-05-31 (Option A CXA-conforms-to-plan + Option B item-12 carve-out sibling)
  - design-phase posture session 2026-05-31 (operator-declared per workspace CLAUDE.md §11.3)
---

# Clearance — `Cross_Axis_Composition_Document v2.18`

v2.18 absorbs the long-carried CXA-OD-IS-EDGE-DRIFT (halt-doc Item 11) by amending §2.3.4 OD→IS bucket from the v2.1-baseline 6-row form (with `U-IS-NN` placeholders + non-resolving IS-spec anchors) to the operator-ratified C3-15 Path (i-refined) 4-row form per OD plan v2.4 §0.4.2. U-OD-27's 2 mis-routed rows (sqlite substrate + ring-buffer eviction) are DELETED as OD-internal; U-OD-30's 2 rows REMAPPED to canonical C-IS-10 anchors; U-OD-20 + U-OD-34 PRESERVED. §2.1 aggregate matrix OD→IS cell 6 → 4; aggregate total 107 → 105. §2.4 per-axis attribution OD outbound 28 → 26 (3 / 3 bucket-coverage preserved).

Council activation was discriminated-out at pre-substantive probe per PR #94 standing-posture amendment 1 (nameable-tension discriminator) — operator already ratified the direction at C3-15 Path (i-refined) Session 3 work; no real CXA-vs-plan voice-tension surfaced; single direction. Per amendment 5 (probe-first discipline), the finding was surfaced as `tension-surfaced + probe-resolved` and operator ratified via single AskUserQuestion. ZERO contract change; ZERO new edge; ZERO production-code change; ZERO cross-axis cascade beyond the §2.3.4 + §2.1 + §2.4 amendment sites.

Sibling PR for halt-doc Item 12 (OD-INTERNAL-FORMALIZATION) authors OD plan v2.27 NEW §4.6 "OD-internal cross-cluster dependency" section per operator AskUserQuestion 2026-05-31 Option (B) carve-out + C3-15 examples. The 2 deleted U-OD-27 rows (sqlite + ring-buffer) become canonical examples at the v2.27 carve-out per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` discipline (refresh-vs-new-authoring sibling shape distinction).

Downstream absorption owed (post-v2.18 per §0.9): workspace `CLAUDE.md` §1.1 OD-axis row refresh + §2.4 CXA row bump + `harness-od/CLAUDE.md` §2.2 + §1.1 refresh + aggregate count refresh. Not patched at this PR per FM-2 single-focus discipline; absorbed at next workspace/per-axis hygiene arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Sibling PR (OD plan v2.27) authored at separate arc per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` — refresh-vs-new-authoring distinction.
- See `.harness/clearance/README.md` for marker discipline.
