# Wave 4 hooks — outcome

*Status record for the U-HK-26..29 "cleanup-family + context-recovery closure" wave.
Source plan: `~/.claude/plans/create-a-very-clear-serialized-wilkes.md`. Reconciliation
that motivated it: `.harness/hook-advisor-workflow-review.md` §9 + §10. Mode-agnostic /
process-substrate. 2026-06-03.*

## TL;DR

Waves 1–3 (U-HK-01..25) shipped the autonomy infrastructure but the §9 reconciliation
found the **cleanup / hygiene / context-recovery back-half** uniformly under-delivered —
the "destructive ops stay explicit" posture had been applied even to *deterministic*
janitorial work, collapsing it to advisory-only (right for HIL, wrong for the unattended
loop). Wave 4 closes that on **"build little, reconcile much":** 3 small build/hardening
units + 1 doc-reconciliation.

## Shipped

| Unit | PR | What | Codex |
|---|---|---|---|
| **U-HK-26** | #274 | Loop-mode **worktree GC** + SessionStart hygiene visibility. `loop_gc_worktrees` reaps merged+clean+non-current+non-main worktrees (worktrees only, never branches); `loop-gc.sh` on SessionStart + `/loop-start`. Closes R-1 + R-5-worktree-half + N-3. | **8 rounds / 11 findings** |
| **U-HK-27** | #275 | **Context-recovery StatusLine** — proactive checkpoint save at 60/75/85% context, chains the operator's themed statusline. Shared `hook_write_checkpoint`. Closes R-3 (corrected from "infeasible"). | round 1 clean |
| **U-HK-28** | #276 | `ruff format --check` in postedit-lint + stop-gate (R-12); explicit hook **timeouts** on blocking Stop + UserPromptSubmit (N-2). | round 1 clean |
| **U-HK-29** | (this) | Doc-reconciliation: review-doc §9 corrections + §10 closure; CLAUDE.md §12.5.3 "resolved checkpoint" = branch-merged; this status doc. | scaled-down (doc) |

## Safety posture

- **U-HK-26 is the highest-blast-radius unit in the workspace** (it deletes worktrees) and
  got the rigor to match: 8 out-of-family Codex rounds caught 11 genuine bugs my own
  review + `advisor()` missed — ignored-file deletion (`.env`/`harness.toml`),
  name-collision reap, symlink self-exclusion, 60-PR-limit, wrong-repo gh, pre-trap
  window. **Worktrees only, never branches** (worktree-remove is reversible; `branch -D`
  is not). Runs as deterministic hook bash → it does **not** bypass the permission guard
  via the agent.
- The locked guardrails are untouched: paid-call / secret-relocation / destructive-git /
  missing-cred still never auto-fire.

## Research-driven correction (operator-supplied, 2026-06-03)

GitHub `anthropics/claude-code#6428` (authoritative; surfaced via operator-supplied Gemini research, not committed here)
established that **`SessionEnd` is unreliable on `/clear`** (fires only when the parent CLI
process is killed; transcript already wiped) and there is **no `PreClear` hook** (#26052).
This *validated* the architecture rather than undermining it: the cleanup that matters
(worktree GC) and the hygiene visibility live on **SessionStart** (reliable), not SessionEnd;
`session-end-cleanup` is minimal/advisory **by design**. Review-doc §10.1 carries the
correction.

## Convergence note (SFA / Ralph loop)

The operator surfaced the [Single File Agents](https://github.com/disler/single-file-agents)
pattern and the [Ralph loop](https://github.com/stevekinney/stevekinney.net/blob/main/writing/the-ralph-loop.md).
Finding: the workspace **already converged on the Ralph loop** — `tools/loop/run.sh`
(U-HK-15) is `while :; do claude -p; done` with all four Ralph guardrails already built
(scope = roadmap next-action; backpressure = CI + hooks; completion = `.loop-halt`; stuck
= `defer.sh`; cap = `HARNESS_LOOP_MAX`), and both the fresh-process (run.sh) and
context-accumulating (stop-loop U-HK-14) variants the article names exist. SFAs are
orthogonal (the *agent*, not the *loop*) and are the right primitive for the **data-pipeline
project**, not the deterministic harness cleanup (which stays hooks).

## Readiness

**Unit-hardened + Codex-reviewed, not yet live-exercised.** "Ready to run" = **ready for a
supervised first run** — iteration cap on, watched — per the Ralph source (`MAX_ITERATIONS`;
"80% is watching and adjusting"). The first real autonomous run is the validation.
