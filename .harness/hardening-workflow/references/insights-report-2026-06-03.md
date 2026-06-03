# Claude Code Insights Report — 2026-06-03 (cross-session corroboration)

> Operator-supplied. Source: `~/.claude/usage-data/report-2026-06-03-173122.html`
> (2,389 messages / 201 sessions / 2026-05-08..2026-06-03). **Independent,
> multi-session evidence** that the failure modes this workflow targets are
> RECURRING, not one-off — plus concrete fix suggestions. Treat as a high-weight
> input alongside `session-evidence.md` (which is this single session's detail).

The report's own framing of the user's workflow: *"an autonomous roadmap-execution
engine… a single 'continue' drives Claude to select the next high-value roadmap
item, ship it as tested atomic PRs, merge, and re-establish a clean fixed point —
repeatedly closing full cycles."* It explicitly calls the human a future *"ratifier
of design forks rather than a driver of implementation."* That IS the loop this
workflow is hardening toward.

## Recurring frictions that map to our disciplines (high weight — multi-session)

- **D6 — defer-paid-when-creds-available (RECURRING, operator-corrected more than
  once).** Verbatim: *"You misapplied the deferred-dependency rule by deferring a
  live paid provider run even though credentials were available, requiring the user
  to correct the rule before work proceeded."* The report's suggested CLAUDE.md
  rule: *"Do not defer paid/live runs when credentials are available — the
  deferred-dependency rule only applies when a real blocker exists."* → Confirms D6
  must be made enforceable, and confirms the operator's corrected rule is the
  intended one. (Caveat for the plan: enforceability must still respect the locked
  paid-call deny as the *unauthorized*-call backstop — see session-evidence D6.)

- **D1 — codex-review stalls + wrong model (RECURRING).** Verbatim: *"A codex run
  stalled 12+ minutes before being killed and used the wrong model (gpt-5.4) due to
  a profile override shadowing the model flag, while codex review queued slowly and
  never returned a verdict before wrap-up."* Suggested fix (a concrete D1 design
  input): *"Before running codex review, echo the resolved model and config, set an
  explicit timeout, and if no verdict returns within N minutes, kill it and proceed
  with a noted caveat."* → The D1 hardening must (a) echo/verify the resolved model
  before launch (guard the profile-override-shadows-flag bug), (b) bound it with an
  explicit timeout, (c) diff-scope it so it's fast enough to actually run, (d)
  define the "kill + proceed with caveat" fallback so a stall doesn't silently skip
  the review entirely (this session's failure).

- **D7 — cwd-bleed + stale cache (RECURRING near-miss).** Verbatim: *"stale
  environment state silently corrupts results… a stale .pyc bytecode cache produced
  misleading no-output results that nearly led to a wrong fork conclusion… and a
  stale settings.json read caused cwd-bleed."* The report names **cwd-bleed**
  explicitly as a recurring class. → Reinforces D7 (the cwd-split guard) AND the
  cache-staleness guard (already AUTO via U-HK-02, but the report shows it still
  bites — verify coverage).

- **§14.2 — [y/n] vs AskUserQuestion (RECURRING).** *"You used text-based [y/n]
  prompts instead of the expected AskUserQuestion interactive menus, requiring user
  correction"* (2+ sessions). → Already a convention; consider whether a
  UserPromptSubmit/Stop hook could detect a Claude-authored `[y/n]` and nudge.

## NEW failure mode (not in session-evidence) — add as D14

- **D14 — output-token-limit resilience in autonomous loops.** Verbatim: *"At least
  6 of your analyzed sessions hit repeated API output-limit errors, making the work
  unrecoverable for review. In autonomous loops this is especially costly since
  context is summarized away."* Suggested fix: *"checkpoint progress to a file
  frequently and keep individual responses concise… so state survives any
  truncation."* This is a real **loop-durability** gap: a long response that hits the
  output cap can lose the iteration's state. The hardened loop should (a) bias toward
  concise responses + frequent durable file checkpoints (the U-HK-05/27 checkpoint
  substrate exists — is it triggered often enough? does the loop write per-step
  progress to a file?), and (b) per CLAUDE.md §14.5, chunk large writes. Capture-failure
  (U-HK-07) logs StopFailure (API errors) — does it capture/recover from an
  output-cap truncation mid-loop? Probably the single most impactful durability fix
  for *unattended* runs.

## Scale / signal (why these matter)
- 13,033 Bash invocations; **252 "Command Failed" + 535 "Other" tool errors** —
  the cwd-split/env-failure class is materially large.
- Tool-error chart: Command Failed 252, Edit Failed 41, File Not Found 34 — the
  git/cwd/file-path failure surface is the dominant error class (D7 leverage).
- The report's "On the Horizon" explicitly describes the target end-state: a
  *"fully overnight autonomous engine that drains an entire roadmap backlog, files
  structured halt docs at genuine ambiguities, and produces a morning report of
  merged PRs and decisions to ratify"* + a *"self-healing test-and-CI hardening
  agent… clears misleading environment signals… only stops when every gate is
  blocking and green."* The hardening plan should keep this end-state in view.

## How the workflow should use this file
- Treat D6, D1, D7, §14.2 corroborations as **raising the priority** of those
  disciplines (they recur across 201 sessions, not once).
- Use the D1 concrete fixes (echo model + timeout + diff-scope + kill-and-caveat) as
  the starting design for the codex-review enforcement.
- Add **D14 (output-token-limit / loop-durability)** to the audited set.
