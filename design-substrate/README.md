# Design Substrate Layout

This directory contains canonical design-phase artifacts. Many files are
versioned delta artifacts whose filenames are cited directly from code,
governance docs, semantic-overlay tooling, and `.harness` audit records.

Do not move or consolidate canonical version files merely to reduce the number
of Markdown files in this directory. Physical reorganization is only safe when
the same arc also updates:

- code/doc cite references to exact filenames,
- semantic-overlay and dashboard readers that scan `design-substrate/`,
- `.harness` back-flow records and clearance markers, and
- any per-axis `CLAUDE.md` / `AGENTS.md` posture references.

Current root-level canonical families:

- `ADR-*`
- `Architectural_Design_Document_*`
- `PRD_*`
- `Spec_*`
- `Implementation_Plan_*`
- `Cross_Axis_Composition_Document_*`
- `Project_Workflow_*`
- Phase-transition manifests and closure handoffs

Older phase artifacts that are no longer current canonical heads may be archived
under `design-substrate/archive/` only when no active cite or tool depends on
their root path.
