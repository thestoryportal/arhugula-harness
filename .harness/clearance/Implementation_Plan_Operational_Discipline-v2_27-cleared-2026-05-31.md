---
artifact: design-substrate/Implementation_Plan_Operational_Discipline_v2_27.md
version: v2.27
cleared_at: 2026-05-31T12:30:00-06:00
clearance_type: implementation-planner-apply-pass
back_reference:
  - .harness/halt-overnight-expansion-2026-05-31.md (Halt-3 — Item 12)
  - design-substrate/Implementation_Plan_Operational_Discipline_v2_4.md §0.4.2 (C3-15 Path (i-refined) deletion record — source for the 2 canonical examples)
  - design-substrate/Cross_Axis_Composition_Document_v2_18.md (sibling PR #110 — halt-doc Item 11 closure)
  - operator AskUserQuestion 2026-05-31 Option (B) carve-out + C3-15 examples ratification
merge_commit: (pending)
reviewer_chain:
  - probe-first empirical orientation at v2.27 arc (PR #94 standing-posture amendment 5)
  - operator AskUserQuestion 2026-05-31 (Option B carve-out + C3-15 examples scope)
  - design-phase posture session 2026-05-31 (operator-declared per workspace CLAUDE.md §11.3)
  - sibling-PR convention per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` (refresh-vs-new-authoring shape distinction; PR #110 is the refresh sibling)
---

# Clearance — `Implementation_Plan_Operational_Discipline v2.27`

v2.27 authors a NEW §4.6.OD-INTERNAL "OD-internal cross-cluster dependency" sub-section per halt-doc Item 12 closure. The section formalizes the distinction between OD-axis-internal cross-cluster composition (within-axis; NOT cross-axis edge) and genuine cross-axis composition (declared at §4.5). Body comprises: (a) definitional carve-out establishing that OD-internal cross-cluster dependencies are NOT cross-axis edges and MUST NOT appear at §4.5.*; (b) 2 canonical examples drawn from the C3-15 Path (i-refined) deletion record at OD plan v2.4 §0.4.2 (U-OD-27 → sqlite substrate + U-OD-27 → ring-buffer eviction); (c) a 4-step discriminator for future cases (target axis residence + contract anchor resolution + hybrid-case handling + canonical declaration path); (d) relation table to existing §3 / §4.5 / §4.6 / §5 OD plan structure.

Scope is **carve-out + examples** per operator AskUserQuestion 2026-05-31 Option (B) ratification, NOT full OD DAG within-axis enumeration. The OD plan's internal DAG remains canonical at the existing §4.6 DAG-traversal content; v2.27's §4.6.OD-INTERNAL is a peer documentation sub-section at the discriminator-dimension layer. ZERO new contract; ZERO new atomic unit; ZERO acceptance criterion change at any existing unit; ZERO cross-axis edge added or removed; ZERO impact on per-OD-contract coverage matrix; ZERO production code change.

Section numbering at §4.6.OD-INTERNAL (sub-section under existing §4.6) preserves delta-only-plan-chain discipline — avoids renumbering disruption at the §4.x chain preserved through v2.26. Sibling PR #110 (CXA v2.18) closes halt-doc Item 11 at the CXA-side cardinality refresh. Both PRs share the operator AskUserQuestion 2026-05-31 design-phase posture session as authority anchor.

Downstream absorption owed (post-v2.27 per §2): `harness-od/CLAUDE.md` §2.3 discriminator cross-reference refresh at next per-axis CLAUDE.md hygiene arc. NOT patched at this PR per FM-2 single-focus discipline.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Sibling PR (CXA v2.18, PR #110) authored at separate arc per `[[advisor-44th-application-dont-bundle-distinct-structural-shapes]]` — refresh-vs-new-authoring shape distinction.
- C3-15 sub-species candidate at workflow doc §7.4.7.2 catalogued at §2 (iii); awaits second instance before workflow-doc promotion per existing catalogue discipline.
- See `.harness/clearance/README.md` for marker discipline.
