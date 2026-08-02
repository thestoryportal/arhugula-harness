---
name: merge-gate
description: Use after out-of-family review and PR CI are green for a substantive arhugula-v2 code or hook PR, immediately before merge.
---

# Merge Gate

Run the repository's three-lens pre-merge gate in fresh Codex contexts. This complements
Antigravity and CI; it replaces neither.

## Scope and preconditions

1. Confirm the PR number, branch, base, and final code HEAD from non-empty Git/GitHub output.
2. Confirm the authorship-dependent out-of-family reviewer approved. For Codex-authored work
   that is Antigravity through `just gemini-review`.
3. Confirm all required checks on the reviewed PR HEAD and current base `main` HEAD are
   terminal green. Confirm no stale prior CI branch remains unresolved; inspect its PR,
   worktree, and unique commits before any cleanup.
4. Inspect the closed changed-file set. Substantive runtime, test, hook, or tool logic uses
   all three lenses. A documentation-only or terminating roadmap refresh may take a logged
   `GATE SKIPPED-PROPORTIONAL`; do not pretend a skip is an approval.

## Three fresh reviewers

Read `.codex/notes/merge-gate-lenses/README.md` and all three lens prompts completely:

- `lens1-concurrency.md`
- `lens2-spec-conformance.md`
- `lens3-test-witness.md`

Launch one fresh, ephemeral, lifecycle-isolated, read-only `codex exec` per lens, preferably in parallel. Each
gets only its lens prompt plus this self-contained tail:

```text
PR under review: #<N> on branch <branch>, base main, head <sha>.
Review the local merge-base diff and enough surrounding source to judge it. Do not edit.
End with exactly VERDICT: APPROVE or VERDICT: BLOCK as the final non-empty line.
```

Use the actual arc worktree with `-C`, `--ephemeral`, `--sandbox read-only`, and a distinct
`--output-last-message /tmp/arhugula-pr-<N>-lens<1|2|3>-<40-char-head>.md`. Put `--`
before the quoted prompt so prompt text cannot be interpreted as an option and the autonomous
permission guard can validate options independently from reviewed text. The prompt must be
one single-quoted literal with no embedded single quote; newlines and shell-looking review
text inside that literal remain data:

```text
env HARNESS_CODEX_REVIEW_ISOLATED=1 codex exec --ephemeral --sandbox read-only -C <arc-worktree> \
  --output-last-message /tmp/arhugula-pr-<N>-lens<1|2|3>-<40-char-head>.md \
  -- '<short instruction to read the named lens file, plus the self-contained tail above>'
```

Validate each invocation separately: exit 0, output file exists and is non-empty, and its
final non-empty line is exactly one permitted verdict. Missing, malformed, truncated, or
ambiguous output is `BLOCK`.

## Outcome

- All three approve: append the PR/date/branch/head/verdicts/outcome row to
  `.harness/merge-gate-log.md`.
- Any block: reconcile it against current HEAD. If real and mechanical, fix it, add the
  appropriate witness, re-run Antigravity and local/CI gates, then re-run the blocking lens
  against the delta. A broad code change invalidates all three approvals.
- Cap automatic fix/re-gate at ten rounds (operator decision, 2026-08-01). An eleventh
  substantive disagreement is a genuine decision point; surface all verdicts together
  rather than looping or choosing silently.

Commit and push the gate-log row before merge, then wait for CI on that final PR HEAD to be
green. The log-only commit does not require re-running approved lenses, but any code, test,
contract, or lens-input change does. Merge only after the final-head CI check and only with
current merge authorization. Re-read the final PR head SHA immediately before merging and
pin the operation with `gh pr merge <PR#> --squash --match-head-commit <final-head-sha>` so
a concurrent push fails closed. Never bypass branch protection.
