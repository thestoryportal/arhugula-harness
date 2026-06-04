# _bmad runtime

Vendored runtime the bmad-* skills depend on. The skills live at
`.claude/skills/bmad-*/` (standard Claude convention, invocable via the Skill
tool). This folder holds only what those skills call at activation. Laid out
per ICM directory discipline.

## What loads what

| File | Loaded by | Why |
|------|-----------|-----|
| `scripts/resolve_customization.py` | every skill, activation step 1 | Merges the 3-layer customize.toml chain and prints JSON. |
| `bmm/config.yaml` | every skill, "Load Config" step | Supplies `{user_name}`, `{communication_language}`, `{document_output_language}`, `{planning_artifacts}`, `{project_knowledge}`, `{project_name}`. |
| `custom/<skill>.toml` | resolver (team layer) | Optional per-skill overrides. Absent by default. |
| `custom/<skill>.user.toml` | resolver (personal layer) | Optional. Absent by default. |
| `artifacts/` | skills (output + scan) | Where generated briefs / PRFAQs / PRDs / research land. Outputs are not committed. |

## How resolution works

A skill at `.claude/skills/bmad-prd/` runs:

```
python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow
```

`find_project_root` walks up from the skill dir until it finds `_bmad/` or
`.git/`, so `{project-root}` resolves to the repo root and this folder is
found. If the script ever fails, each skill has a documented manual fallback:
read `customize.toml` directly and use its defaults. The install degrades
gracefully either way.

## Canonical sources

- Config values: `bmm/config.yaml` (this is their one home).
- Per-skill defaults: each skill's own `customize.toml`.
- Provenance, license, and the optional cross-skill references that are NOT
  installed: see `README.md`.
