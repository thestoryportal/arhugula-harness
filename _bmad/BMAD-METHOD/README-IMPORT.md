# BMAD-METHOD — imported workflow directories

Source: https://github.com/bmad-code-org/BMAD-METHOD (default branch, cloned 2026-06-04)

Scope imported: **workflow directories and their contents, excluding skills** (per operator instruction).

In this version (v6) of BMAD-METHOD the methodology is organized as *skills*; "workflows"
and skills are largely the same construct. Repo-wide, only ONE methodology directory is
literally named `workflows/`:

- `bmm-skills/1-analysis/bmad-document-project/workflows/` — imported here (path preserved for context).
  Contains: deep-dive-workflow.md, deep-dive-instructions.md, full-scan-workflow.md, full-scan-instructions.md.

Deliberately EXCLUDED:
- `.github/workflows/` — GitHub Actions CI for the BMAD repo itself (not a methodology workflow).
- Skill directories (SKILL.md / instructions.md / templates / checklist.md) — excluded per "other than skills".
- Workflow-related FILES that are not directories: `docs/**/reference/workflow-map.md`, test fixtures,
  `tools/format-workflow-md.js`, website workflow-map diagrams.

NOTE: BMAD v6's "34+ workflows" (README) are implemented AS skills. If the intent was those,
that is the skills layer, which was excluded here by instruction.
