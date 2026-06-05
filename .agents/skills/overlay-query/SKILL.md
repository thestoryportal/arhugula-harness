---
name: overlay-query
description: Use for arhugula-v2 semantic-overlay cite grounding: resolving C-*, U-*, H_T-*, ADR-*, CXA, or section cites to implementation files, checking seam producer/consumer grounding, or verifying cross-spec drift before claims.
---

# Overlay Query

Use this skill instead of free-text search when the task depends on a formal design cite, atomic unit, substitution row, or CXA seam.

## Workflow

1. Read root `AGENTS.md` startup rules and the nearest axis `AGENTS.md` if the cite is axis-specific.
2. Prefer the repo overlay command:

```bash
just overlay-query <cite-or-pattern>
```

3. If the command needs a different syntax, inspect `justfile` and the relevant overlay script before retrying.
4. Use raw `rg` only for non-cite text searches or after the overlay has identified candidate files.
5. In the answer, distinguish overlay-grounded facts from inferences made from nearby code.

## Guardrails

- Do not claim that a file implements a `C-*`, `U-*`, `H_T-*`, or CXA contract without overlay grounding or direct file evidence.
- If overlay results contradict a spec, plan, or `CLAUDE.md` carry, stop and classify the drift instead of absorbing it silently into implementation.
- For PR-ready work, include the relevant overlay/targeted test evidence in the PR body or final report.
