---
artifact: design-substrate/<filename>
version: v<X.Y>
cleared_at: <ISO-8601 timestamp with TZ, e.g., 2026-05-29T15:30:00-06:00>
clearance_type: <one of: P3a-CK | P3-CK | P5-CK | P6-CK | Phase-7-absorbed-via-fork-doc | Phase-7-absorbed-via-architect-recommendation | Phase-7-absorbed-via-retirement-event | spec-writer-apply-pass | doc-hygiene-refresh>
back_reference:
  - <link to .harness/* doc or PR # that authorized this clearance>
  - <e.g., .harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md>
  - <e.g., PR #37>
merge_commit: <git SHA, short form acceptable>
reviewer_chain:
  - <one item per layer that participated in clearance>
  - <e.g., council voices C1 + C5 + C9 (CP-axis subset)>
  - <e.g., harness-adversarial-reviewer Phase 7 pre-impl review>
  - <e.g., operator AskUserQuestion ratification {date} Q-set>
  - <e.g., spec-writer apply pass>
  - <e.g., impl-time grounding pass at force-push pre-merge revision>
supersedes: <optional — filename of prior marker this one supersedes>
superseded_by: <optional — filename of newer marker that supersedes this one>
---

# Clearance — `<Artifact name> v<X.Y>`

<One-paragraph narrative: what changed in this version of the artifact and why.>

<Optional second paragraph: what was reviewed during clearance, any deferrals or carve-outs, sub-arcs still open.>

<Optional third paragraph: any caveats for Phase 7 consumers — e.g., partial clearance, surfaces that remain in-flight, follow-on work expected.>

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
