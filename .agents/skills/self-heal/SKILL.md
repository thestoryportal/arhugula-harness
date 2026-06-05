---
name: self-heal
description: Use when the operator says /self-heal, get the suite green, fix the build, tests are flaky, or asks Codex to restore a verified green state for arhugula-v2.
---

# Self Heal

Use this skill only to restore or verify a green fixed point, not to add features.

## Workflow

1. Inspect `git status --short --branch` and avoid touching unrelated user changes.
2. Read `AGENTS.md`, `justfile`, and relevant axis `AGENTS.md`.
3. Reproduce the failure with the narrowest command that shows it.
4. Classify failures as environment artifact, stale generated state, test bug, or genuine logic defect.
5. Fix only genuine defects or stale test expectations that are contradicted by current authoritative guidance.
6. Re-run the failing target until stable, then broaden to `just check` for PR-ready changes.

## Evidence Standard

- Capture the exact failing command and the exact passing command.
- Do not claim flakiness without repeat evidence.
- If sandbox/network restrictions prevent a meaningful check, report the blocked command and why.
