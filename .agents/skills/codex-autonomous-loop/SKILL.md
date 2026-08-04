---
name: codex-autonomous-loop
description: Use when Codex must drive an arhugula-v2 coding arc through isolated implementation, validation, review, GitHub CI, merge, refresh, cleanup, and continuation.
---

# Codex Autonomous Loop

Maintain one evidence-bound controller loop from live roadmap state through the next fixed
point. Do not claim an arc complete merely because code or PR CI is green.

## Start

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
just codex-autonomous-arc <arc-id>
```

Run this from a clean linked worktree, never the shared root. The untracked
`.harness/codex_loop_state.json` is evidence for the current run. Each record is bound to
branch, HEAD, linked-worktree identity, and worktree fingerprint.

## Controller and implementers

For a multi-leg arc, preserve the Claude Fable 5-orchestrator/Opus 5-implementer split:
the interactive controller runs `gpt-5.6-sol` at high reasoning through
`--profile arhugula-forward`, while each fresh implementer runs `gpt-5.6-terra` at high
reasoning through `codex exec --profile arhugula-implementer`. Give each implementer exactly
one brief based on `.codex/notes/leg-brief-template.md` and one isolated worktree. Cap
concurrent implementers at two. Every brief includes the operator
decision verbatim, authority, owned files, deliverables, negative examples, STOP-if-premise-
false rule, tests, and report shape. The controller reads each actual diff; self-reports are
not acceptance evidence.

## Required gate order

1. `worktree_ready`: prove clean linked worktree and current-main base.
2. `preflight`: run `just codex-preflight`.
3. `plan`: record owned scope, authority, RED witness, verification, and tracking surfaces.
4. `red`: observe the expected failure; record `status=failed`.
5. `implementation`: smallest complete scoped change.
6. `narrow_verify`: targeted witness passes, including mutation/real-path proof where owed.
7. `local_gate`: `just codex-check`, plus overlay/shell/live gates required by the claim.
8. `decorrelated_review`: when Codex authored, run `just gemini-review` through the
   OAuth-authenticated Antigravity `agy` CLI only and require the report to end
   `VERDICT: APPROVE`; never use provider API keys, service-account/Vertex routing, or a direct
   API call. Standing operator authorization covers the subscription and current-diff disclosure
   for all forward work, so do not ask again. When Claude authored, use
   `just codex-review`. Resolve real findings and re-run changed gates.
9. `closeout`: run `just codex-closeout`.
10. `commit`: explicit paths only; never `git add -A`; record commit SHA and scope.
11. `push`: push the exact topic branch and validate remote state.
12. `pr_opened`: PR body includes exact checks, skipped checks, and tracking surfaces.
13. `ci_green`: every required check on final PR HEAD and the current base `main` HEAD is
    terminal green. Inventory other open/remote topic branches before merge; if a stale prior
    branch exists, reconcile its PR/worktree/unique-commit state without deleting work.
14. Before merge, execute the `merge-gate` skill: three fresh Codex contexts, one per
    concurrency, spec-conformance, and test-witness lens. All approve; append and commit the
    `.harness/merge-gate-log.md` row; wait for final-HEAD CI again.
15. `merged`: merge only with current authorization and `--match-head-commit`; never bypass.
16. Wait for the merge SHA's own main CI to be green. No forward work starts before this.
17. `post_merge_refresh`: land the immediate roadmap-status-only terminating refresh, or
    record a narrowly justified non-applicability for a refresh itself.
18. Wait for the refresh merge's own main CI to be green.
19. `main_synced`: local `main` equals final `origin/main`.
20. Reflect and run the gstack `context-save` skill.
21. Emit the arc exit report (U-WT-03/04) WHILE the arc worktree still exists — its
    ledger carries this arc's pending-HIL rows, which disposition deletes:
    `just arc-exit-report --pr <NNN> --merge-sha <merge-sha> --checkpoint <the-path-context-save-just-reported>`
    (run from the arc worktree; the report and its index land in the MAIN checkout).
    Require exit 0 and the named report path — a nonzero exit includes a failed
    `EXIT-REPORT` index append and fails this gate closed. Skip only for a pure
    terminating-refresh PR.
22. `worktree_disposition`: original worktree is unregistered; only the verified merged
    local topic branch is pruned; remote branch hygiene is resolved without losing work.
23. Run the full `just codex-loop-check` — it unconditionally requires the
    `worktree_disposition` gate, so it can only pass AFTER step 22 (running it earlier
    always exits 1).

Record gates with:

```bash
just codex-loop-record --phase <phase> --status <status> \
  --command "<exact command>" --evidence "<result tied to current diff/HEAD>"
```

If the diff changes after any pre-commit gate, re-record that gate and all downstream
pre-commit gates. If the PR HEAD changes after a reviewer/lens approval, re-review the delta
and wait for CI on the new head. Checkpoint prose never overrides current Git or GitHub state.

## Review layers

- Implementer self-check is not independent.
- The controller validates the diff and witnesses.
- Antigravity is the out-of-family artifact reviewer for Codex-authored work.
- The fresh three-lens merge gate is mandatory for substantive code/hook PRs and complements,
  rather than replaces, Antigravity and CI.
- Any BLOCK is reconciled against current HEAD, fixed if real, and re-gated. Malformed or
  empty reviewer output fails closed.

## Stop conditions

Stop only for a genuine operator decision, a credential/paid-call boundary, an unauthorized
irreversible/outward action, a falsified arc premise, or a gate that remains red after honest
diagnosis. Unknown commands, missing evidence, pending CI, and reviewer parse failures are
not success. Record the blocker and exact resume action; otherwise continue to the fixed
point and then initialize the next roadmap arc.
