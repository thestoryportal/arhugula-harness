# `.harness/clearance/` — design-substrate clearance markers

This directory holds records of `design-substrate/` artifact versions that have been cleared for Phase 7 consumption.

## Purpose

Phase 7 sessions consume `design-substrate/*` as canonical. When a design-substrate artifact changes (new spec version, plan revision, ADR amendment), Phase 7 should not silently consume the new version — the change must have been operationally accepted via documented back-flow first.

A clearance marker is the record of that acceptance. It pins a specific version of a specific artifact and names what authorized the version to be consumed.

The X-AL-3 silent-absorption guard (`.github/workflows/x-al-3-guard.yml`) recognizes any file under `.harness/clearance/` as back-flow documentation; including a marker in the same PR as a `design-substrate/` edit satisfies the guard.

## When to file a marker

File a marker when one of:

- An original P5-CK / P6-CK adversarial review clears a new spec / plan (greenfield Phase 5 / Phase 6 arcs)
- A Phase 7 in-flight revision is absorbed into canonical (spec amendment apply-pass merged to main)
- A retirement-event filing includes spec doc-hygiene refresh
- An architect recommendation triggers a spec / plan revision that lands on main
- A Class 1 fork ratification + spec-writer apply pass lands on main

Filing is part of the same PR that lands the design-substrate change. If you forget to file the marker, the X-AL-3 guard will fail the PR with a pointer to this README.

## Filename convention

```
.harness/clearance/{artifact-slug}-v{version}-cleared-{YYYY-MM-DD}.md
```

The artifact slug is the design-substrate filename stem with underscores preserved. The version is the artifact's authored version. The date is the date the clearance event occurred (typically the PR merge date, but the marker may be drafted before merge).

### Examples

- `.harness/clearance/Spec_Control_Plane-v1_26-cleared-2026-05-29.md`
- `.harness/clearance/Implementation_Plan_Operational_Discipline-v2_26-cleared-2026-05-28.md`
- `.harness/clearance/ADR-D5-v1_4-cleared-2026-05-20.md`
- `.harness/clearance/Cross_Axis_Composition_Document-v2_16-cleared-2026-05-28.md`

## Marker shape

See `TEMPLATE.md` in this directory. Frontmatter + body. Body is 1-3 paragraphs of narrative.

## Phase 7 consumption discipline

When a Phase 7 skill / session reads a `design-substrate/` artifact, it SHOULD verify a matching clearance marker exists. The verification surface:

```bash
# example check — does CP spec v1.26 have a clearance marker?
ls .harness/clearance/Spec_Control_Plane-v1_26-cleared-*.md
```

Missing marker → halt + route to operator for clearance. This discipline is enforced at the skill body level (each skill that consumes design-substrate references this convention); the CI guard enforces only the file-presence aspect (back-flow documentation must accompany design-substrate edits).

## Retroactive markers

In v1 of this convention, markers are NOT retroactive for the back-catalog of design-substrate artifacts pre-2026-05-29. The implicit clearance for back-catalog is: "merged to main on or before 2026-05-29 and not subsequently invalidated by a fork doc." Going forward from 2026-05-29, every spec / plan / ADR / ADD / PRD / CXA version amendment SHOULD include a clearance marker in the same PR.

If retroactive markers are desired for traceability, they may be added in standalone PRs labeled `design-phase-direct` (so the X-AL-3 guard passes without requiring a paired design-substrate edit).

## Supersession

When a new version of an artifact is cleared, the old marker remains in this directory as historical record. The new marker supersedes it. Phase 7 sessions consume the *latest* marker for an artifact. The historical markers serve as an audit trail of version progression.

A marker is never deleted. If a clearance is invalidated (e.g., a Class 3 fork retroactively invalidates a prior clearance), the marker is updated with a `superseded_by:` field in frontmatter pointing at the new marker.

## See also

- Workspace `CLAUDE.md` §4 — substitution + back-flow discipline
- Workspace `CLAUDE.md` §4.4 — X-AL-3 anti-leakage rule
- `Project_Workflow_v1_12.md` §2 — phase definitions + checkpoint clearances
- `Project_Workflow_v1_12.md` §4 — fork classes + revision triggers
- `.github/workflows/x-al-3-guard.yml` — CI enforcement
