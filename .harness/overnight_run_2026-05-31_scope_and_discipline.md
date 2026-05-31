# Overnight Autonomous Run — 2026-05-31 → 2026-06-01

**Operator:** Robert Rhu (asleep)
**Model:** Claude Opus 4.7 (1M context)
**Mode:** Non-HITL autonomous via `/loop` self-paced
**Anchor:** workspace CLAUDE.md §10.9 standing posture + §11 posture declaration + §4.4 X-AL-3 anti-silent-absorption

## Scope fence (HARD)

Three permitted work categories. Anything else = HALT + file `.harness/halt-{n}.md`.

### Category A: Pre-merge adversarial reviews (read-heavy + report-write)

PRs #93, #94, #95 already merged at start of this run. No pre-merge reviews owed against them. However, if NEW PRs open during the run (e.g., this loop's own hygiene PRs), apply pre-merge adversarial review per workspace CLAUDE.md §10.9 amendment 1 + harness-adversarial-reviewer skill standing-posture amendment 1.

**Skip Category A if no new PRs are open at iteration start.**

### Category B: Per-axis CLAUDE.md hygiene sweep (well-bounded edits)

Refresh CXA version pointers at 3 per-axis CLAUDE.md files to CXA v2.17 (current canonical per workspace CLAUDE.md §2.4). Files in scope:

- `harness-cp/CLAUDE.md` — §1.1 + §2.3 + §2.4 cite-shape rows (currently at v2.15 per checkpoint Q5)
- `harness-od/CLAUDE.md` — §2.x CXA cite (currently at v2.9 per checkpoint Q5)
- `harness-is/CLAUDE.md` — §2.x CXA cite (currently at v2.1 per checkpoint Q5)

**Edit shape:** single-line row bumps + minimal narrative refresh where semantically accurate (e.g., aggregate counts 101→107; CP outbound 63→69 at harness-cp). NO §4.1 retirement-status prose changes (those are sub-stale but require operator-discretion ratification per workspace pattern).

**One PR per file** (or one bundled PR; loop's discretion based on diff cleanliness). PR title pattern: `hygiene: refresh harness-{axis}/CLAUDE.md CXA cites to v2.17`.

### Category C: Pattern-catalogue + workspace memory audit (read-only + single report write)

Audit the 50+ workspace memory entries at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` for:

1. **Cardinality drift** — entries claiming pattern cardinality N where current HEAD shows N+k or N-k
2. **PR # references** — entries citing PR #N where the PR's actual state on origin/main differs from the memory's claim
3. **Phantom references** — entries citing files, symbols, or units that no longer exist at HEAD
4. **Stale STATUS-line claims** — entries with status framings (e.g., "OPEN", "PARTIAL", "RETIRED") where the actual ledger state diverges

**Output:** single file `.harness/memory_audit_2026-05-31.md` listing flagged entries with: (a) memory file path, (b) stale claim, (c) current HEAD reality, (d) suggested closure shape (refresh / close / supersede / preserve). NO memory edits.

**One PR for the audit report.** Title: `audit: workspace memory entries 2026-05-31`.

## HALT conditions (immediate)

On hitting any of these, write `.harness/halt-{n}.md` with: reason, what was attempted, what's needed from operator. Then move to next scope-fence item (do not retry).

1. **Any `design-substrate/**` edit attempted** — workspace CLAUDE.md §4.4 X-AL-3 hard rule
2. **Any `harness-*/src/**` edit attempted** — Phase 7 implementation territory; needs operator scope ratification
3. **Any new PR open beyond the scope-fence categories** — out-of-scope work
4. **Any Class 1 fork surfaced** — needs operator AskUserQuestion ratification per workspace CLAUDE.md §4.3
5. **Any AskUserQuestion need (any question that would warrant operator decision)** — file the question at halt-{n}.md as a "questions for operator" block
6. **Test failure surfaced during a hygiene PR** — write halt; do not push the PR with failing tests
7. **Empirical-state contradicts checkpoint claim** — e.g., per-axis CLAUDE.md not at the version this doc claims. Write halt with the divergence; let operator route in the morning

## Git workflow discipline (e2e)

Per iteration:

1. **Sync main:** `git fetch origin main` + verify worktree is on a clean state branched off the latest commit on `origin/main`
2. **Branch creation:** `git checkout -b <task-slug-kebab-case>` where slug captures the task (e.g., `hygiene-harness-cp-claude-md-cxa-v2-17`)
3. **Work + commit:** edit files in scope; `git add <specific files>` (NEVER `git add -A`); commit with conventional-commit message + Co-Authored-By footer per CLAUDE.md commit convention
4. **Push:** `git push -u origin <branch>`
5. **Open PR:** `gh pr create --title "..." --body "..."` per workspace PR template (Summary + Test plan + ZERO change attestations + Co-Authored-By footer)
6. **Auto-merge gate:** before merging, verify (a) X-AL-3 guard PASS via `gh pr view --json statusCheckRollup`, (b) merge state CLEAN, (c) no scope-fence violations in the diff
7. **Merge if safe:** `gh pr merge <pr#> --squash --delete-branch`
8. **Checkout main + pull:** `git checkout main && git pull` to sync local
9. **Worktree cleanup:** if working in `.claude/worktrees/h-t-is-2-architect-rec`, stay here; no new worktrees needed (each task uses its own branch within this worktree)

## Checkpoint discipline

After every PR open (whether merged or halted): run `/context-save` to record state. Filename should reflect the iteration + outcome (e.g., `20260531-0900-hygiene-harness-cp-merged`).

## Final action at queue exhaustion

When all scope-fence items are complete (or all skipped via halt):

1. Run `/context-save` with a comprehensive end-of-run summary at filename `20260531-XXXX-overnight-run-complete.md`
2. Write a final summary at `.harness/overnight_run_2026-05-31_summary.md`:
   - What was attempted
   - What landed (with PR numbers + commit shas)
   - What halted + why
   - Questions for operator (consolidated from all halt-{n}.md files)
   - Recommended next action for morning-Robert
3. Exit the loop gracefully (no further ScheduleWakeup)

## Anti-anti-patterns (DO NOT)

- DO NOT touch `design-substrate/**` — workspace CLAUDE.md §4.4 hard rule
- DO NOT touch `harness-*/src/**` — Phase 7 territory
- DO NOT open AskUserQuestion (operator is asleep) — halt instead
- DO NOT auto-merge a PR that has any test failure, X-AL-3 guard failure, or merge-state-status non-CLEAN
- DO NOT continue retrying a halted item in subsequent iterations — file the halt and move on
- DO NOT skip /context-save between iterations — context preservation is the load-bearing discipline
- DO NOT inflate scope by "while I'm here..." additions — strict fence discipline

## Work queue (ordered)

1. Category C (memory audit) — read-only + single report PR; lowest risk; do first
2. Category B item 1 — `harness-cp/CLAUDE.md` CXA v2.15 → v2.17 refresh
3. Category B item 2 — `harness-od/CLAUDE.md` CXA v2.9 → v2.17 refresh
4. Category B item 3 — `harness-is/CLAUDE.md` CXA v2.1 → v2.17 refresh
5. Category A (only if NEW PRs are open at this point) — pre-merge adversarial review

Self-pace via ScheduleWakeup. Default interval between iterations: 30 minutes (1800s). Adjust shorter if work is queued; longer if waiting for external state (e.g., GitHub PR check propagation).

## Recovery if loop crashes

Latest `/context-save` snapshot under `~/.gstack/projects/.../checkpoints/` is the recovery anchor. Next session can resume via `/context-restore` and pick up the work queue from wherever it stopped.

---

*End of overnight run scope + discipline. File path: `.harness/overnight_run_2026-05-31_scope_and_discipline.md`. Reference from /loop prompt.*
