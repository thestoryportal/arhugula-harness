---
name: codex-autonomous-loop
description: Use when driving an arhugula-v2 coding arc through the Codex controller/coder/validator/CI/closeout loop.
---

# Codex Autonomous Loop

Use this skill when the operator asks Codex to run an implementation arc with autonomous loop discipline.

## Roles

- Controller: owns repo context, plans, HIL gates, integration, and final claims.
- Coder: makes scoped edits and records the commands it ran.
- Spec validator: reviews the diff against the stated requirements and rejects under-build or over-build.
- Quality validator: reviews the diff for bugs, regressions, missing tests, and maintainability.
- External reviewer: `just codex-review` is mandatory for PR-ready diffs; `just coderabbit-review ...` is optional advisory review.

Validators review artifacts and evidence, not the coder's summary.

## Invocation

Start an arc:

```bash
just codex-autonomous-arc ARC_ID
```

Record gates:

```bash
just codex-loop-record --phase plan --status passed --command "plan accepted" --evidence "controller checklist written"
just codex-loop-record --phase red --status failed --command "uv run pytest ..." --evidence "expected RED before implementation"
just codex-loop-record --phase implementation --status passed --command "apply_patch ..." --evidence "scoped files changed"
just codex-loop-record --phase narrow_verify --status passed --command "uv run pytest ..." --evidence "targeted tests passed"
just codex-loop-record --phase local_gate --status passed --command "just codex-check" --evidence "provider-free PR gate passed"
just codex-loop-record --phase decorrelated_review --status passed --command "just codex-review" --evidence "review issues resolved or none"
just codex-loop-record --phase closeout --status passed --command "just codex-closeout" --evidence "context guard closeout passed"
```

Check readiness:

```bash
just codex-loop-check
```

Loop records include branch, HEAD, and a worktree fingerprint. If code changes
after implementation, verification, review, or closeout evidence is recorded,
re-record that gate and every downstream gate before claiming completion.

## Required Gate Order

1. `preflight`: `just codex-preflight` in the linked worktree.
2. `plan`: concise controller plan with file scope, tests, and tracking surfaces.
3. `red`: a failing test or witness before implementation. The recorded status must be `failed`.
4. `implementation`: minimal scoped code/docs changes.
5. `narrow_verify`: targeted tests proving the changed behavior.
6. `local_gate`: `just codex-check` or a documented narrower gate for docs-only changes.
7. `decorrelated_review`: `just codex-review`; optionally add `just coderabbit-review ...`.
8. `closeout`: `just codex-closeout`.

## Prompt Templates

Coder prompt:

```text
You are the coder for this arhugula-v2 arc. You are not alone in the codebase.
Do not revert unrelated edits. Own only these files: <FILES>. Requirements:
<REQUIREMENTS>. First add or preserve the RED witness, then make the smallest
change that passes it. Return changed paths and exact commands run.
```

Spec validator prompt:

```text
Review the diff against these requirements only: <REQUIREMENTS>. Do not trust
the coder summary. Check for missing requirements, extra behavior, design/impl
mixing, tracking-surface obligations, and RED-without-fix evidence. Return
blocking issues first with file/line references.
```

Quality validator prompt:

```text
Review the diff for bugs, regression risk, missing tests, unsafe state handling,
and maintainability. Do not restate strengths unless no issues exist. Return
critical/important/minor issues and concrete fixes.
```

## Stop Conditions

- HIL/operator gate requested by the operator or required by repo policy.
- Failed RED witness that does not fail for the expected reason.
- Validator reports unresolved critical or important issues.
- `just codex-loop-check`, `just codex-check`, `just codex-review`, or `just codex-closeout` fails.
- Paid provider, credential, destructive, or network-sensitive work lacks explicit authorization.
