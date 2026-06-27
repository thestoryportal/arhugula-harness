---
name: codex-autonomous-loop
description: Use when driving an arhugula-v2 coding arc through the Codex controller/coder/validator/CI/GitHub shipping/closeout loop.
---

# Codex Autonomous Loop

Use this skill when the operator asks Codex to run an implementation arc with autonomous loop discipline.

## Roles

- Controller: owns repo context, plans, HIL gates, integration, and final claims.
- Coder: makes scoped edits and records the commands it ran.
- Spec validator: reviews the diff against the stated requirements and rejects under-build or over-build.
- Quality validator: reviews the diff for bugs, regressions, missing tests, and maintainability.
- External reviewer: `just codex-review` is mandatory for PR-ready diffs; `just coderabbit-review ...` is optional advisory review.
- Shipping controller: owns commit, push, PR, CI, merge, post-merge refresh, main sync, and worktree disposition evidence.

Validators review artifacts and evidence, not the coder's summary.

## Invocation

Start an arc:

```bash
just codex-autonomous-arc ARC_ID
```

Record gates:

```bash
just codex-loop-record --phase worktree_ready --status passed --command "git worktree ..." --evidence "linked worktree and branch based on current origin/main"
just codex-loop-record --phase plan --status passed --command "plan accepted" --evidence "controller checklist written"
just codex-loop-record --phase red --status failed --command "uv run pytest ..." --evidence "expected RED before implementation"
just codex-loop-record --phase implementation --status passed --command "apply_patch ..." --evidence "scoped files changed"
just codex-loop-record --phase narrow_verify --status passed --command "uv run pytest ..." --evidence "targeted tests passed"
just codex-loop-record --phase local_gate --status passed --command "just codex-check" --evidence "provider-free PR gate passed"
just codex-loop-record --phase decorrelated_review --status passed --command "just codex-review" --evidence "review issues resolved or none"
just codex-loop-record --phase closeout --status passed --command "just codex-closeout" --evidence "context guard closeout passed"
just codex-loop-record --phase commit --status passed --command "git commit ..." --evidence "commit sha and exact scope"
just codex-loop-record --phase push --status passed --command "git push -u origin ..." --evidence "remote branch pushed"
just codex-loop-record --phase pr_opened --status passed --command "gh pr create ..." --evidence "PR number and URL"
just codex-loop-record --phase ci_green --status passed --command "gh pr checks --watch ..." --evidence "blocking CI checks green"
just codex-loop-record --phase merged --status passed --command "gh pr merge ..." --evidence "merged PR number and merge sha"
just codex-loop-record --phase post_merge_refresh --status passed --command "refresh PR or not-applicable note" --evidence "terminating refresh merged or explicitly not applicable"
just codex-loop-record --phase main_synced --status passed --command "git pull --ff-only" --evidence "local main equals origin/main"
just codex-loop-record --phase worktree_disposition --status passed --command "git worktree remove ... or retained" --evidence "clean removed worktree or explicit retention reason"
```

Check readiness:

```bash
just codex-loop-check
```

Loop records include branch, HEAD, linked-worktree status, and a worktree
fingerprint. If code changes after implementation, verification, review, or
closeout evidence is recorded, re-record that gate and every downstream
pre-commit gate before committing. After commit, the shipping gates become the
required downstream evidence before claiming the loop complete.

## Required Gate Order

1. `worktree_ready`: linked worktree and branch are confirmed before edits.
2. `preflight`: `just codex-preflight` in the linked worktree.
3. `plan`: concise controller plan with file scope, tests, and tracking surfaces.
4. `red`: a failing test or witness before implementation. The recorded status must be `failed`.
5. `implementation`: minimal scoped code/docs changes.
6. `narrow_verify`: targeted tests proving the changed behavior.
7. `local_gate`: `just codex-check` or a documented narrower gate for docs-only changes.
8. `decorrelated_review`: `just codex-review`; optionally add `just coderabbit-review ...`.
9. `closeout`: `just codex-closeout`.
10. `commit`: intentional commit with explicit scope.
11. `push`: branch pushed to origin with upstream set.
12. `pr_opened`: PR opened with verification, skipped checks, and tracking-surface notes.
13. `ci_green`: blocking PR checks observed green.
14. `merged`: PR merged per GitHub discipline.
15. `post_merge_refresh`: terminating refresh PR merged, or an explicit not-applicable note.
16. `main_synced`: local main fast-forwarded to the merged remote state.
17. `worktree_disposition`: worktree removed if safe, or retained with a clear reason.

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
- `just codex-loop-check`, `just codex-check`, `just codex-review`, `just codex-closeout`, PR CI, merge, main sync, or worktree disposition fails.
- Paid provider, credential, destructive, or network-sensitive work lacks explicit authorization.
