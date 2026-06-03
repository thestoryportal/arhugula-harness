# Wave 2 hooks — outcome

*Status record for the U-HK-11..17 "loop-mode autonomy" wave of the hooks plan
(`~/.claude/plans/let-s-brainstorm-adding-additional-recursive-taco.md` §Wave 2).
Mode-agnostic / process-substrate. 2026-06-03.*

## TL;DR

**All 7 Wave 2 units shipped** (U-HK-11..17), authorized by the operator via
AskUserQuestion ("build full Wave 2" → "retry hard blocked items" → "push all"). Every
autonomy behavior is **OFF by default** behind the `loop_mode_active()` gate, with a
hard-stop deny-list enforced even in loop mode. 18/18 hook test suites green.

## Shipped

| Unit | What | Test | Wiring |
|---|---|---|---|
| **U-HK-11** | loop-mode flag + `.harness/loop_status.md` ledger + `/loop-start`·`/loop-stop` skills (`loop_lib.sh`) | 14/14 | skills |
| **U-HK-12** | guardrailed auto-approve (`PreToolUse`/`PermissionRequest`, tri-state: deny-list → allowlist → ask) | 19/19 | settings.json |
| **U-HK-13** | Codex+Advisor decision resolver (`/resolve` skill + `resolve_lib.sh`) | 6/6 | skill |
| **U-HK-14** | in-session Stop-continue loop (iteration cap + halt marker) | 11/11 | settings.json |
| **U-HK-15** | headless overnight runner (`tools/loop/run.sh` + `just loop`) | 9/9 | recipe |
| **U-HK-16** | git-arc-guard (advisory Stop reminder: uncommitted/unpushed/behind-origin) | 6/6 | settings.json |
| **U-HK-17** | subagent self-validation (SubagentStart contract + SubagentStop retry guard) | 7/7 | settings.json |

Markers (`.loop-active` / `.loop-iter` / `.loop-halt`) + the ledger are gitignored
runtime artifacts.

## Safety posture

- **OFF by default.** Nothing auto-drives unless loop mode is explicitly on
  (`HARNESS_LOOP=1` or `.harness/.loop-active`, set by `/loop-start` or `just loop`). A
  normal interactive session never sees an auto-decision.
- **Hard-stop deny-list, even in loop mode** (U-HK-12): paid LLM/MCP calls, force-push /
  history-rewrite / branch-delete, recursive `rm`, secret/credential relocation,
  provider network calls, creds-requiring recipes — denied + logged, never auto-fired.
  Preserves `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`.
- **Bounded** (U-HK-14/15): the Stop-continue loop caps at `HARNESS_LOOP_MAX` (default
  25) turns; the headless runner caps iterations; both stand down on a
  `.harness/.loop-halt` gate marker.
- **Default = ask.** Unknown tools fall through to the normal approval prompt (deny in
  headless). Fail-safe by construction.
- **Reversible-only auto-decisions** (U-HK-13): `/resolve` auto-decides only reversible
  in-repo forks via two decorrelated reviewers (out-of-family Codex + transcript-aware
  advisor); paid/secret/destructive/missing-cred forks defer to the operator.
- **No `--dangerously-skip-permissions`** in the headless runner; approvals flow through
  the permission guard.

## Provenance note

The auto-approve + headless units triggered the Claude Code auto-mode safety classifier
(which guards against an agent finalizing its own approval-bypass). They landed only
with explicit, specific operator authorization (AskUserQuestion) and the operator
switching to accept-edits mode + directing the push — i.e., the human exercised
authority the agent does not hold unilaterally. The boundary did its job: this tier of
autonomy infrastructure is operator-gated by design, not agent-self-serve.

## Operating it

`/loop-start` (or `just loop`) turns loop mode on; `/loop-stop` turns it off. Review
`.harness/loop_status.md` after any run — `DEFERRED-HIL` / `DENY` / `RESOLVE-SPLIT` rows
are the things that wanted a human. The fully-autonomous loop remains an explicit,
reviewable, bounded opt-in.

## Pre-merge hardening (out-of-family Codex review)

PR #268 was driven through the `just codex-review` (gpt-5.5, out-of-family) gate to
practical convergence — **12 rounds, ~30 genuine bypasses fixed**, almost all on the
auto-approve guard (`permission-guard.sh`, the highest-blast-radius unit). The guard
ended up: tri-state (deny-list → allowlist → ask) and inert off loop-mode; allowlisting
only commands that are safe *regardless of arguments* (dev/git arc + pure builtins),
dropping content-readers + path-mutators (the loop uses the structured Read/Edit/Grep/Glob
tools, which enforce `_safe_path` with physical symlink-chain resolution); deny-list
covering force-push / history-rewrite / branch-delete+force-move / recursive-rm / secret
relocation / paid provider calls / `gh pr merge --admin` / `git commit --amend`; secret/
worktree/`.git`/traversal/env-expansion arg rejection; bounded loop (cap + halt marker +
signal trap with TERM→KILL escalation).

### Known residuals (operator-accepted 2026-06-03, AskUserQuestion)

Three round-12 findings were accepted rather than fixed, because their guard-level fixes
would gut core loop function while the risks are already mitigated. All only matter *in
loop mode* (an explicit opt-in):

1. **Broad `Grep` / `git diff` could surface an in-tree secret.** Mitigated: the Grep tool
   is ripgrep (respects `.gitignore`) and `git diff` only shows *tracked* files — so
   gitignored secrets (this repo's convention) are never surfaced. Residual = a *committed
   plaintext secret*, which is a repo-hygiene failure outside the guard's scope.
2. **`pytest` / `just test` can make real provider calls** if a key is in the env and the
   repo's e2e tests run. Mitigated/accepted: the loop's own `claude -p` is paid by design,
   so enabling loop mode IS a paid opt-in; the only guard-level fix is "don't auto-run
   tests," which defeats verify-before-commit. Operators who want zero incidental calls can
   run the loop without a provider key in env (e2e tests then skip).

These are documented residuals, not silent gaps. Tightening them further is a follow-on
option (remove pytest/git-diff/grep from auto-allow) if an operator prefers maximum
restriction over loop autonomy.
