# _bmad

Minimal vendored runtime for the five BMad analysis + planning skills installed
under `.claude/skills/`. Only the dependencies those five skills call at runtime
live here. The full BMAD-METHOD repo is intentionally not pulled in.

## Installed skills (at `.claude/skills/`)

- `bmad-technical-research`
- `bmad-product-brief`
- `bmad-prfaq`
- `bmad-agent-pm`
- `bmad-prd`

## Provenance

- Source: https://github.com/bmad-code-org/BMAD-METHOD (`src/bmm-skills/`),
  branch `main`. License: MIT (c) 2025 BMad Code, LLC.
- `scripts/resolve_customization.py` is vendored verbatim from
  `src/scripts/resolve_customization.py` of that repo. Stdlib only
  (`argparse`, `json`, `sys`, `pathlib`, `tomllib`); requires Python 3.11+.
  No `pip install`, no `uv`.
- BMad, BMad Method, and BMad Core are trademarks of BMad Code, LLC. Vendoring
  these files does not grant trademark rights.

## Contents

```
_bmad/
  CONTEXT.md          routing: what loads what
  README.md           this file
  scripts/
    resolve_customization.py   3-layer customize.toml merge (vendored)
  bmm/
    config.yaml       runtime values the skills read ({user_name}, etc.)
  custom/             optional per-skill overrides (empty by default)
  artifacts/          generated outputs land here (not committed)
```

## Optional cross-skill references NOT installed

The five skills suggest invoking other `bmad-*` skills at certain points (help
menus, deeper elicitation, editorial polish, downstream handoffs). Those skills
are part of the wider BMAD-METHOD repo and were deliberately not pulled in. The
references degrade gracefully: when an uninstalled skill is invoked, the step is
skipped and the gap is noted. They are not missing installs. The set:

`bmad-help`, `bmad-advanced-elicitation`, `bmad-party-mode`,
`bmad-editorial-review-structure`, `bmad-editorial-review-prose`,
`bmad-generate-project-context`, `bmad-brainstorming`, `bmad-market-research`,
`bmad-domain-research`, `bmad-create-architecture`, `bmad-create-epics-and-stories`,
`bmad-check-implementation-readiness`, `bmad-correct-course`, `bmad-quick-dev`,
`bmad-ux`, `bmad-workflow-builder`.

To add any later, install it under `.claude/skills/` the same way; no `_bmad/`
change is required (each skill carries its own `customize.toml`).
