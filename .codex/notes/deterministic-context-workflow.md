# Deterministic Codex Context Workflow

Codex must not rely on remembered workflow state for load-bearing claims. This
note is the source of truth for preventing context rot, drift, and hallucinated
closeout in Codex sessions for this repository.

## Operating Principle

Every substantive Codex arc materializes state from repository instruments at
defined gates. Memory, checkpoints, prior chat, and dashboard prose are
orientation only until re-grounded against HEAD.

The `just` recipes are the mandatory command surface. Direct
`tools/codex_context_guard.py` invocation is equivalent only when it uses the
same mode and flags.

## Required Gates

### 1. Preflight

Run before substantive work:

```bash
just codex-preflight
```

The preflight materializes:

- repository root, cwd, branch, HEAD, and linked-worktree status
- dirty status and changed files
- roadmap dashboard hash versus computed workspace hash
- open fork-doc count and latest retirement batch
- dashboard snapshot freshness when dashboard sources changed
- a local checkpoint artifact at `.harness/.checkpoints/codex-context-latest.json`

Hard failures stop work until resolved.

### 2. Edit Gate

All edits occur in isolated Codex worktrees. The root checkout is read/status
only. If the guard sees edits in the root checkout, the arc is invalid.

Do not mix design/spec/plan/fork-doc changes with implementation/test changes
unless the operator explicitly requested a design-phase/back-flow arc.

### 3. Cite Gate

For `C-*`, `U-*`, `H_T-*`, `ADR-*`, or CXA seam claims:

```bash
just overlay-query ...
```

Use `rg` for sibling `design-substrate/**` prose drift because the semantic
overlay intentionally does not scan sibling spec bodies.

### 4. Drift Recheck

After long work, merges, rebases, or context transition, rerun:

```bash
just codex-preflight
```

Treat memory/checkpoint "remaining work" as advisory until rechecked against
the current dashboard, git state, and source files.

For an explicit mid-arc checkpoint:

```bash
just codex-checkpoint mid-arc
```

The checkpoint records the current context fingerprint, HEAD, branch, changed
files, status entries, dashboard state, and findings. It is ignored by git and
exists to make context-refresh moments inspectable rather than remembered.

### 5. Closeout

Run before final response, commit, or PR:

```bash
just codex-closeout
```

Closeout checks:

- worktree-only edit discipline
- design/implementation boundary
- dashboard hash drift on the default branch
- stale committed human dashboard snapshot when dashboard sources changed
- cite-bearing changes that require `just overlay-check`
- missing tracking-surface review
- fresh checkpoint match against current HEAD/status/dashboard

The closeout recipe first writes a `pre-closeout` checkpoint, then runs the
closeout guard with `--require-fresh-checkpoint`. A stale or missing checkpoint
is a hard failure when freshness is required.

### 6. Tracking Surface Audit

No substantive task is complete until required tracking surfaces are updated or
explicitly reported as not applicable:

- `Project_Roadmap_v1.md`
- `.harness/roadmap_status.md`
- `tools/dashboard/roadmap.html`
- `.harness/substitutions.yaml`
- retirement batches under `.harness/phase-7d-retirement-events-batch-*.md`
- fork docs under `.harness/class_*_fork_*.md`
- axis `CLAUDE.md` / `AGENTS.md` files when posture changes
- clearance markers for design/spec/plan amendments
- memory entries when a pattern reaches the memory threshold

The PR body or final response must report implementation status, verification,
tracking updates, and any owed follow-on refresh.

## Tool Contract

`tools/codex_context_guard.py` is the deterministic checker. It has three modes:

```bash
just codex-preflight
just codex-checkpoint <label>
just codex-closeout
just codex-context-check
```

`codex-context-check` is the combined hard gate for local validation. It exits
nonzero on hard violations and requires a fresh checkpoint. CI runs the guard
directly without local checkpoint freshness because `.harness/.checkpoints/` is
intentionally untracked.

The Codex `SessionStart` and `Stop` hooks invoke the same guard. Hook failures
propagate nonzero when the guard reports a hard finding or cannot run.
