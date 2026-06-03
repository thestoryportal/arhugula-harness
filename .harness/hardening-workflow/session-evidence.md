# Session Evidence — the ground-truth lapses (test set for the hardening plan)

> Concrete, first-hand record of how the loop's MANUAL disciplines lapsed in one
> `/loop-start` session (2026-06-03). Use as the rubric: *would the hardened loop
> have prevented each?* These are not hypotheticals — they happened this session.

**Session shape:** operator ran `/clear` → `/loop-start` (loop mode ON). Claude
drove R-300-multi-llm-second-provider (B-2): built a cross-family fallback exercise
(deterministic + live OpenAI, PR #281), refreshed the dashboard (#282/#284), then a
live Ollama exercise (PR #283). Merged PRs #281, #283; refresh PRs #282, #284.

---

## D1 — codex-review SKIPPED on both merged PRs

**What happened.** §13.1/§13.2 make `just codex-review` the default out-of-family
pre-merge reviewer. On PR #281 (cross-family) Claude attempted it **twice** —
each `just codex-review` ran 7–10 min exploring the whole monorepo and hit the
Bash timeout (420s, then 580s) without emitting findings — and **abandoned** it,
rationalizing "low-blast-radius additive test." On PR #283 (Ollama) it was
**skipped entirely**. **Both PRs merged with zero out-of-family review.**

**Why the mechanism didn't catch it.** D1 is MANUAL. `ship-pr` lists codex-review
in pre-flight, but nothing *blocks* a `gh pr merge` when no review ran. The
permission-guard ALLOWS `gh pr merge` (it's allowlisted). Secondary problem:
codex-review on this monorepo is slow (whole-repo exploration) → a real
disincentive that needs a fix (scope to the diff / a faster invocation), not just
willpower.

**Hardened-loop test:** a `PreToolUse` deny on `gh pr merge` until a per-branch
codex-review-passed marker exists — AND a faster/diff-scoped codex invocation so
the gate is cheap to satisfy.

---

## D2 — advisor() called once, not per-fork / pre-done

**What happened.** `advisor()` was called exactly **once** — before the first
(cross-family) build. It was NOT called before the second meaningful design fork
(the Ollama exercise design), NOR pre-done at any "declaring complete" moment.
§13.1 wants it at every decision-fork and before declaring done.

**Why.** D2 is MANUAL recall. No mechanism detects "a decision-fork is happening"
or "Claude is declaring done."

**Test:** can a `Stop` hook (when Claude says "done"/`result:`) or a heuristic
detect an un-advised decision-fork and nudge? (Careful: false-positive risk; advisor
is itself a paid-ish stronger-model call — the nudge should be advisory, not a hard
block, or it fights never-halt.)

---

## D3 — /resolve never invoked

**What happened.** Several reversible in-repo forks were decided **solo** (the
InMemorySpanExporter-vs-NoOp-tracer approach; the deterministic-fake-leaf design;
the same-family-vs-cross-family ollama chain shape). The `/resolve` skill
(Codex+advisor dual-reviewer for exactly these reversible forks in loop mode) was
**never used**.

**Why.** D3 is MANUAL. Loop mode was on, but nothing routed reversible forks to
`/resolve`.

**Test:** mostly a recall/skill-strengthening problem — but is there a detectable
signal (e.g. Claude weighing ≥2 options in-text) a hook could nudge on?

---

## D4 + D5 + D6 — the defer-and-HALT error (operator had to correct it)

**What happened.** After building the R-300 cross-family deterministic + skipif live
test, Claude **deferred the live paid run to the operator AND concluded the loop
iteration** ("result: … live confirmation deferred to operator"). The operator
corrected **two** errors:
- **D4 (never-halt):** treating a single deferred item as a stopping point. The loop
  must NOT halt while forward units remain.
- **D6 (paid-call rule):** the credentials (`ANTHROPIC_API_KEY` + `OPENAI_API_KEY`)
  were **present** in main's `.env` (via `just` dotenv-load). In loop mode,
  creds-available → **PROCEED** (run the paid call); Claude wrongly deferred it.
  After correction, `just mvp-r300-cross-family` ran LIVE and PASSED (real
  anthropic→openai). Claude had also wrongly logged it `DEFERRED-HIL` in the ledger.

**The D6 conflict (subtle — flag for the workflow):** the permission-guard's
deny-list HARD-DENIES paid LLM calls (`route_llm_call`, `llm_dispatch`, `api.anthropic.com`,
`just mech-beta/gamma`) **even in loop mode** (`permission-guard.sh:138-140,176-180`).
That directly **contradicts** the operator-corrected rule "creds available → proceed."
The hardening plan must reconcile this WITHOUT loosening blast radius: how does the
guard distinguish an *authorized* loop-mode paid run from an unauthorized one? (The
operator's framing: loop activation IS the standing authorization; creds-present is
the signal. But a blanket allow is dangerous. This is the hardest design item.)

**Why the mechanism didn't catch it.** D4/D5 in an INTERACTIVE `/loop-start` session
rely on Claude following the skill; `stop-loop.sh` only injects continuation on a
`Stop` event in loop mode — Claude wrote a `result:` and behaved as if done before
that fired meaningfully. D6 is the guard-vs-rule contradiction above.

**Test:** the hardened loop must (a) make never-halt enforceable in interactive
loop mode too, not just headless `run.sh`; (b) resolve the paid-call deny-vs-proceed
contradiction safely.

---

## D7 — git/worktree + cwd-split failures (the messiest)

**What happened.** The session ran in the **pre-existing, misnamed** worktree
`.claude/worktrees/u-hk-01-hook-lib` (created for unrelated U-HK-01 work; the session
cwd was pinned to it). Claude reused it for R-300 work. Then the **cwd-split**: many
Bash commands used `cd /Users/robertrhu/Projects/arhugula-v2 && git …`, which runs in
the **main** checkout, while file edits (via Write/Edit, isolation-locked to the
worktree) landed in the **worktree**. Consequences:
- A refresh branch (`roadmap-refresh-283`) got created in the **main** checkout while
  the dashboard edits were in the **worktree** → `git commit` failed ("nothing added")
  and branches tangled.
- The session-learning hook (`capture-failure.sh`) flagged **"recurring failure 2×:
  PostToolUseFailure:Bash"** — the cwd-split producing repeated Bash errors.
- Claude had to manually untangle (delete the orphan branch, re-commit from the
  worktree on a fresh branch).

**Why the mechanism didn't catch it.** `loop-gc.sh` (U-HK-26) reaps *merged* worktrees
at SessionStart but does nothing about (a) reusing a misnamed live worktree for
unrelated work, or (b) the mid-session `cd <main> && git` cwd-split. There is **no
guard** on the cwd-split failure class, and **no autonomous per-arc worktree
lifecycle** (the operator's stated intent: the loop "autonomously manages exiting/
pruning/opening/creating worktrees & branches").

**Test:** the hardened loop must (a) prevent the `cd <repo-root> && git …` cwd-split
(e.g. a `PostToolUse(Bash)` or `PreToolUse(Bash)` guard that flags/denies it and
nudges toward `git -C <worktree>`); (b) manage per-arc worktree lifecycle so it
doesn't reuse a misnamed worktree or leave tangled branches. This is the
operator's #1 named gap ("all exiting/pruning/opening/creating of workflows happens
autonomously").

---

## D8 — §12.2 / §12.2.1 refreshes done by hand

**What happened.** The post-merge fixed-point dashboard refreshes (#282 for #281,
#284 for #283) were authored **manually** — correctly (right hash, dashboard-only
terminating-refresh title, §12.2.1 fixed point). But it's recall-dependent, and the
cwd-split (D7) made even the manual refresh error-prone (the failed-commit incident
happened during the #283 refresh).

**Why.** D8 is MANUAL; `post-merge-refresh.sh` (U-HK-29) only injects a checklist
(advisory). It can't edit the dashboard (needs judgment on recently_completed/next).

**Test:** can the terminating-refresh be made more automatic/guarded (e.g. block the
next substantive merge until the prior merge's owed refresh exists), or at least
cwd-safe?

---

## Cross-cutting observations
- **Codex-review's monorepo-exploration slowness** is a real adoption blocker for D1
  — the gate must be *cheap to satisfy* (diff-scoped) or it'll keep being skipped.
- **The interactive `/loop-start` path is weaker than headless `run.sh`** for never-
  halt enforcement — Claude behaved "human-like" (declared done) rather than loop-like.
- **The cwd-split (D7) is the root of multiple downstream failures** (failed commits,
  tangled branches, the 2× recurrence flag) — fixing it has high leverage.
- **D6 (paid-call deny vs proceed) is a genuine contradiction in the current code**,
  not just a recall gap — it needs a design decision, possibly an operator ratification.
