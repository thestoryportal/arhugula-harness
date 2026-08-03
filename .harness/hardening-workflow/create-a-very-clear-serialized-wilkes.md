# Plan — Wave 4: cleanup-family + context-recovery closure (U-HK-26..29)

> **Historical implementation plan.** U-HK-26 originally specified loop-mode reaping at
> SessionStart. Later parity hardening superseded that trigger: SessionStart is report-only
> in every mode; explicit post-merge/closeout and `/loop-start` calls own safe reaping.

## Context

**Why.** The §9 reconciliation in `.harness/hook-advisor-workflow-review.md` found the shipped hooks-autonomy infra (Waves 1–3, U-HK-01..25) robustly handles the *forward-drive* half (auto-approve, resolver, Stop-continue) but uniformly under-delivers the *cleanup / hygiene / context-recovery back-half* — because the correct "destructive ops stay explicit" posture was applied even to janitorial units, collapsing them all to advisory-only. That is right for HIL (a human reads the report) and wrong for the autonomous loop (no human; cruft accumulates — proven by this very session sitting in a stale merged worktree).

**Correction that reshaped this plan.** Primary-source verification (operator-directed: the claudefa.st 10-section hooks series + official `code.claude.com/docs/en/{hooks,statusline}`) overturned three claims my Explore subagents produced and I had propagated:
- **R-3 (token-threshold proactive save) is FEASIBLE, not infeasible** — `StatusLine` receives `context_window.used_percentage` / `remaining_percentage` / `total_input_tokens` / `context_window_size` / `exceeds_200k_tokens` on stdin every turn (claudefa.st §8 "context-recovery-hook" is the reference pattern). It moves from "document-as-infeasible" to a real **build**.
- **`/clear` fires BOTH `SessionStart(source=clear)` AND `SessionEnd(reason=clear)`** — the worktree gap's real cause is advisory-by-design + a hook can't remove the worktree it runs inside, not a missing SessionEnd.
- **`UserPromptExpansion` is a real event** (the semantically-precise trigger for skill-activation), not a phantom.

**Outcome.** Close every §9 finding (Sev A→D) on the principle **build little, reconcile much**: 3 small build/hardening units + 1 doc-reconciliation unit, restoring the missing worktree-GC + context-recovery features without weakening any locked guardrail (paid / secret / destructive-git / missing-cred still never auto-fire).

---

## Findings → disposition (the spine)

| Finding | Disposition | Unit |
|---|---|---|
| **R-1** worktree/branch prune never happens (advisory + invisible) | **BUILD** loop-mode worktree GC + HIL visibility | U-HK-26 |
| **R-3** token-threshold proactive save (CORRECTED: feasible) | **BUILD** StatusLine context-recovery | U-HK-27 |
| **R-12** no `ruff format --check` | **BUILD** (hardening) | U-HK-28 |
| **N-2** blocking Stop/UPS hooks lack explicit timeouts | **BUILD** (hardening) | U-HK-28 |
| **N-3** MEMORY.md over cap, advisory-only/invisible | **BUILD** surface at SessionStart | U-HK-26 |
| **R-2** checkpoint "archive resolved" unbuilt + split-brain | **RECONCILE** (+ trivial `rm→mv`) | U-HK-29 |
| **R-4** stop-gate lint-only vs planned `just check`+task-verify | **RECONCILE** (lint-only is correct; task-verify optional) | U-HK-29 |
| **R-5** git-arc-guard advisory vs planned "enforce" | **RECONCILE** (worktree-orphan half → U-HK-26) | U-HK-29 + D2 |
| **R-6/R-7/R-8** settled deviations (Codex-both / defer-continue / sync) | **RECONCILE** (record authoritative) | U-HK-29 |
| **R-9/R-11/R-13/R-14** cosmetic (names / event / matcher / proxy) | **RECONCILE** (note; R-11: UserPromptExpansion is real → optional move per D4) | U-HK-29 |
| **R-15** plan open-items | already closed — **RECORD** | U-HK-29 |

Net: **4 units.** All `tools/**` + `.claude/settings.json` + docs — mode-agnostic process-substrate, zero `design-substrate/**`, zero `src/**` (X-AL-3 trivially clean). Continues the workspace's `U-HK-NN` one-unit-per-PR + hermetic-test discipline.

---

## Atomic units

### U-HK-26 — Loop-mode worktree GC + hygiene visibility  *(closes R-1, R-5-worktree-half, N-3)*
**What (historical design; current trigger superseded by the banner above).** A `loop_gc_worktrees()` function + a `loop-gc.sh` hook on **SessionStart** (the originally proposed uniform reaping point — fires for live-loop sessions, each headless `claude -p` child, and post-`/clear`; self-excludes the current worktree so it only reaps *prior* sessions' leftovers).
- **Loop mode (`loop_mode_active`) → ACTION:** for each worktree in `git worktree list --porcelain` that is (a) **not** the current `git rev-parse --show-toplevel`, (b) **not** main, (c) its branch ∈ the merged set, (d) clean (`git -C <wt> status --porcelain` empty) → `git worktree remove <path>`. **Worktrees only — never `git branch -d/-D`** (worktree removal is reversible; merged branch refs are harmless and the irreversible force-delete is left to the operator). Append each removal/skip to `.harness/loop_status.md` via `loop_log`.
- **HIL mode → VISIBILITY:** emit `additionalContext` listing stale-merged-worktree count + merged-branch `git branch -d` candidates + a MEMORY.md over-cap flag (fixes the invisible-SessionEnd-report problem).
- **Fail-safe:** if `gh` is empty/errors (offline, no remote), the merged set is empty → **zero removals** (never delete on uncertainty).
**Reuse (don't reinvent).** The squash-merge-safe merged-branch cross-ref already exists at `tools/hooks/session-end-cleanup.sh:35,41-44` (`gh pr list --state merged --json headRefName` × `git for-each-ref`) — lift it into `loop_lib.sh`. Use `loop_log` (`tools/hooks/loop_lib.sh`), `loop_mode_active`/`hook_bounded`/`hook_project_dir` (`tools/hooks/lib.sh`).
**Design constraint (load-bearing).** The GC runs as **deterministic hook bash, never a Claude tool call** — `permission-guard` hard-denies `git worktree remove`/`git branch -d` *for Claude's tool calls*, but hook-script bash bypasses the guard. This is why it lives in a hook + `loop_lib.sh`, not in agent actions.
**Files.** `tools/hooks/loop_lib.sh` (+`loop_gc_worktrees`), `tools/hooks/loop-gc.sh` (new), `.claude/settings.json` (SessionStart array; second hook alongside the audit), `tools/hooks/test_loop_gc.sh` (new, hermetic — fixture repo with a fake merged worktree + a dirty one + the current one; assert only the merged+clean+non-current is removed, gh-empty → no-op, HIL → report-not-delete). Optional call sites: `tools/loop/run.sh` between iterations + `tools/hooks/stop-loop.sh` at halt.
**AC.** Reaps merged+clean+non-current+non-main worktrees in loop mode; never branches; never the current worktree; gh-empty → no-op; HIL mode reports candidates (no deletion); ledger-logged; hermetic test green; `bash -n` clean.

### U-HK-27 — Context-recovery StatusLine  *(closes R-3 — the corrected build)*
**What.** A `statusLine` command (claudefa.st §8 pattern) that on every turn reads `context_window.used_percentage` (+ `total_input_tokens`) from stdin and triggers a **proactive checkpoint save** when crossing thresholds (e.g. 60% / 75% / 85% used, deduped via a small state file `~/.claude/.harness-statusline-state.json` keyed on session id), reusing the existing `precompact-checkpoint.sh` snapshot writer (`.harness/.checkpoints/`). Complements PreCompact (boundary save) by saving *earlier*. Renders a compact context%/cost line as the visible status bar (D3).
**Compose, don't clobber (tension).** A user-level statusline already exists at `~/.claude/statusline-command.sh` / `~/.claude/statusline.sh`; the project has none. The new command must **chain** the existing one (run it, append our segment) or be opt-in, never overwrite the user's global config. Confirm at build.
**Files.** `tools/statusline/context-recovery.sh` (new), `.claude/settings.json` (`statusLine` block — new), refactor the snapshot-writing core of `tools/hooks/precompact-checkpoint.sh` into a shared helper both call, `tools/statusline/test_context_recovery.sh` (new, hermetic — feed synthetic stdin JSON at 50/65/80% and assert save-fires-once-per-threshold + state-file dedupe + chains the prior statusline + never blocks).
**AC.** Parses `context_window.used_percentage`; fires one proactive save per crossed threshold (no duplicates via state file); reuses the precompact writer; composes with any pre-existing statusline; fast (<300ms, no network); renders a context bar; hermetic test green.
**Note.** Pairs with the shipped U-HK-06 `postcompact-reinject.sh` for the full save→restore context-recovery loop.

### U-HK-28 — Hook hardening: ruff-format + explicit timeouts  *(closes R-12, N-2)*
**What.** (a) Add `ruff format --check` alongside `ruff check` in `tools/hooks/postedit-lint.sh` (advisory) and `tools/hooks/stop-gate.sh` (block-on-fail) — closes the planned-but-dropped "+ format check". (b) Add explicit `timeout` values in `.claude/settings.json` to the blocking hooks (the 3 on `Stop`, the 3 on `UserPromptSubmit`) so a hung hook can't stall a turn (no explicit timeout today; default is long).
**Files.** `tools/hooks/postedit-lint.sh`, `tools/hooks/stop-gate.sh`, `.claude/settings.json`, extend `tools/hooks/test_postedit_lint.sh` + `tools/hooks/test_stop_gate.sh` (assert format violation is flagged/blocked; clean passes).
**AC.** Format violations surfaced (postedit) / block (stop-gate); clean files silent; explicit timeouts present on all blocking hooks; existing 18 hook suites stay green.

### U-HK-29 — Reconciliation: plan + CLAUDE.md + review-doc  *(closes R-2, R-4, R-5-doc, R-6/7/8/9/11/13/14/15)*  — **doc-only**
**What.** "Reconcile much" — align the docs to the (mostly-correct) as-built, and correct my own earlier errors:
- **Review-doc `§9` corrections (owed):** R-3 "infeasible" → **feasible-via-StatusLine** (built at U-HK-27); strike the "/clear doesn't fire SessionEnd" root-cause; R-11 "phantom event" → **real event** (`UserPromptExpansion`).
- **R-2:** in CLAUDE.md §12.5.3 define **"resolved checkpoint" = its `branch:` is in the merged set** (the same squash-safe cross-ref); accept precompact keep-10 as correct for thin snapshots; *optionally* change `session-end-cleanup.sh`'s precompact `rm` → `mv .harness/.checkpoints/archive/` (trivial, closes the literal AC). Do **not** stand up two-system resolved-detection machinery (lowest value).
- **R-4:** record that lint-only-per-turn is the correct scope (heavy `just check` stays in CI); the claudefa.st §4 "Stop task-enforcement" half (verify open tasks complete) is an **optional** future add via the real `TaskCompleted` event or a Stop-time `TaskList` check — note, don't build.
- **R-5:** per D2 — keep git-arc-guard advisory-by-design; note the worktree-orphan half is now closed by U-HK-26.
- **R-6/7/8:** record as settled deviations (already in the plan Status + CLAUDE.md §13.1/§13.2 / PR #272 / sync-fix).
- **R-9/R-11/R-13/R-14:** note cosmetic; for R-11 record `UserPromptExpansion` as the precise event (optional move per D4).
- **R-15:** record closed.
- Update the hooks plan's Status block + bump the workspace roadmap (`Project_Roadmap_v1.md` Surface VII / autonomy-infra cluster gets the U-HK-26..29 entries) + `.harness/roadmap_status.md` per §12.2.
**Files.** `.harness/hook-advisor-workflow-review.md` (§9 corrections + a new §10 "Wave-4 closure"), `~/.claude/plans/let-s-brainstorm-adding-additional-recursive-taco.md` (Status: note Wave 4), `CLAUDE.md` §12.5.3 (**via PR, never silent** — per U-HK-20 / §11), `Project_Roadmap_v1.md`, `.harness/roadmap_status.md`.
**AC.** Every §9 finding has an explicit recorded disposition; no doc still asserts R-3-infeasible or the wrong /clear cause; CLAUDE.md change rides a reviewable PR; roadmap refreshed to the §12.2.1 fixed point.

---

## Decision points (recommended defaults — override at plan review)

- **D1 — GC scope (U-HK-26):** *worktrees-only* **(recommended; reversible, safety-sound)** vs. also force-delete merged branches. Advisor-flagged: branch force-delete is the only irreversible step and squash-merge forces `-D`; the original gap was a worktree.
- **D2 — git-arc-guard (R-5):** *stay advisory* **(recommended; worktree-orphan half now closed by U-HK-26)** vs. make it `decision:block` at Stop on orphaned state (stronger, but false-blocks intentional mid-arc pauses).
- **D3 — StatusLine scope (U-HK-27):** *proactive-save + a compact visible context bar* **(recommended)** vs. save-only (no visible bar). Either way it must compose with the existing `~/.claude/statusline*.sh`.
- **D4 — skill-activation event (R-11):** *keep `UserPromptSubmit`* **(recommended; works, silent-when-correct)** vs. move U-HK-21 to the semantically-precise `UserPromptExpansion` (fires only on command expansion — less per-prompt work). Low stakes either way.

---

## Primary-source anchors (so the build cites real APIs)

- StatusLine stdin fields: `context_window.{used_percentage,remaining_percentage,total_input_tokens,total_output_tokens,context_window_size,current_usage}`, `exceeds_200k_tokens`, `cost.total_cost_usd`, `rate_limits.*` — `code.claude.com/docs/en/statusline` §Available-data.
- Hook events (30) incl. `SessionStart(source: startup|resume|clear|compact)`, `SessionEnd(reason: clear|logout|…)`, `PreCompact(trigger: manual|auto)`, `UserPromptExpansion`, `WorktreeCreate/Remove`, `TaskCompleted` — `code.claude.com/docs/en/hooks`.
- claudefa.st series: §8 context-recovery (R-3 ref impl), §7 session-lifecycle, §4 stop-task-enforcement (R-4), §9 skill-activation (UserPromptExpansion), §10 permission-hook.

## Verification (end-to-end)

- **Per unit:** hermetic test (synthetic stdin payloads / fixture repo, the `test_post_merge_refresh.sh` pattern) → `bash -n` → existing 18 hook suites stay green → `just codex-review` (out-of-family) → CI green → merge → §12.2.1 terminating refresh.
- **U-HK-26 live gate:** `/loop-start`, open a 2nd session in main → confirm the stale `u-hk-01-hook-lib` worktree is reaped (and **only** it); confirm gh-offline → no-op; confirm HIL mode reports-not-deletes.
- **U-HK-27 live gate:** feed the statusLine synthetic JSON crossing 60/75/85% → a checkpoint appears in `.harness/.checkpoints/` once per threshold; the prior user statusline still renders.
- **Guardrail regression:** with loop mode on, confirm `permission-guard` still hard-denies a paid/secret/destructive op and the GC never touches an unmerged/dirty/current worktree.

## Owed immediately after plan-mode (can't edit in plan mode)

Correct `.harness/hook-advisor-workflow-review.md` §9 (R-3 feasible; /clear cause; R-11 real) — folded into U-HK-29 but flagged here so it isn't lost.
