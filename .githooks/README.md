# Git hooks

This directory holds shared git hooks for the workspace.

## Enable

Run once per local checkout:

```bash
git config core.hooksPath .githooks
```

After this, the hooks in this directory are active for the local repo. Per-checkout setup (rather than global) is intentional: different repos have different hook needs.

## Hooks

### `pre-commit`

**WO-U06 trial commit gate, then the X-AL-3 advisory check.** The hook first runs `tools/workflow_commit.py pre-commit --root <worktree>`. It exits 0 for legacy work, which continues unchanged; for a trial-profile unit it checks the commit's actual staged scope and blocks the commit unless that passes. A worktree can select the trial profile only when this directory is its `core.hooksPath`, because otherwise Git would not run the gate. Git's own bypasses (`--no-verify`, another `core.hooksPath`) skip it; required CI still runs.

**X-AL-3 advisory check.** Warns if `design-substrate/*` is staged without an accompanying `.harness/` back-flow doc. Non-blocking — the enforceable gate is the GitHub Action at `.github/workflows/x-al-3-guard.yml`.

Background: per workspace `CLAUDE.md` §4.4 (X-AL-3 anti-leakage rule) + Workflow §2.7.6, design changes at Phase 7 execution time must route through documented back-flow (fork doc, architect recommendation, retirement event, or clearance marker). The hook gives early local feedback so you don't push a PR that will fail CI.

If the hook fires:

- Add a `.harness/class_N_fork_<slug>.md` or `.harness/architect_recommendation_<slug>.md` or similar
- OR add label `design-phase-direct` to the PR after pushing
- OR proceed and let CI catch the problem (the hook is advisory)

## Disable

```bash
git config --unset core.hooksPath
```

This reverts to the default `.git/hooks/` directory (which is untracked).
