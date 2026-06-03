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
