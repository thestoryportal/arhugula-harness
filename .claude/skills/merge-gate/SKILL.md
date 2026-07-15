---
name: merge-gate
description: Decorrelated 3-lens pre-merge review gate — launches three parallel Agent-tool subagents (concurrency/race-conditions, spec-conformance-against-ledgers, test-witness-adequacy) against a PR's diff, each returning a structured APPROVE/BLOCK verdict. Use right after CI is confirmed green and `just codex-review` has converged, before running `gh pr merge`, for any code-touching PR in the /loop continue → ship-pr flow. Do NOT use on doc-only or `ops: roadmap status refresh` PRs — skip those entirely; the gate only fires when the diff touches `harness-*/src|tests` (or equivalent code surface). Merge only when all three verdicts are APPROVE; any BLOCK or split verdict halts the merge and surfaces the disagreement via AskUserQuestion.
---

# merge-gate — decorrelated 3-lens pre-merge review

An **addition** to the existing pre-merge apparatus (`just codex-review` + `advisor()`), not a
replacement. It composes with `ship-pr`'s pre-flight — see the wiring note at the end.

## Honesty caveat — read this before trusting an all-approve

The three subagents below are Claude Agent-tool subagents: **lens-decorrelated, not
vendor-decorrelated.** Same model family, same training-time blind spots. Their value is that
each goes *deep on one specialty* the generic pass skips, not that they're independent eyes in
the way Codex (`just codex-review`, out-of-family, $0 subscription) or `advisor()`
(transcript-aware) are. This gate does **not** replace either — it runs alongside them. If a
finding matters and you want real cross-vendor confidence, that's still Codex's job.

This gate is **instruction-level, not a hard hook.** `permission-guard.sh` is a shell script —
it cannot launch subagents. Enforcement here is the loop agent following this documented
procedure, exactly as reliable as that compliance. It is not a mechanical block the way the
deny-list is.

## Scope gate — skip non-code PRs

Before doing anything else, check the PR's changed files (`gh pr diff <PR#> --name-only` or
equivalent). If the diff is **doc-only** or is a **terminating refresh PR**
(`ops: roadmap status refresh …`, touching only `.harness/roadmap_status.md`) — **skip this
gate entirely.** Running a concurrency/test-witness reviewer on a status-refresh PR is pure
waste and a spurious-block risk. Fire only when the diff touches `harness-*/src/**`,
`harness-*/tests/**`, or equivalent runtime code (hooks, tools scripts with real logic).

## The three reviewers — launch in ONE message, three parallel Agent calls

Each prompt must be **self-contained** (a subagent sees only what you write — no conversation
context) and must include the PR's diff or a pointer to fetch it
(`gh pr diff <PR#>`), the branch name, and the specific lens. Generic "review this PR" prompts
just triplicate what Codex already does — go deep on the specialty, explicitly forbid a
generic pass, and demand a machine-parseable verdict line.

**Reviewer 1 — concurrency / race conditions:**
> Review this diff for concurrency defects only — do not do a general code review. Diff:
> `gh pr diff <PR#>` on branch `<branch>`. Look specifically for: race conditions on shared
> state; TOCTOU races in file/git operations; deadlock/livelock potential; incorrect
> `asyncio.timeout`/cancellation handling (CancelledError raised *inside* the timeout block vs
> a bare `TimeoutError` from an inner coroutine outside it — these are different failure
> shapes); non-atomic check-then-act patterns; daemon-reused context leaking across concurrent
> runs (needs per-run isolation, not a shared frozen object); fence/step-id keys that could
> double-fire on a changed step_id. For each concern found, cite file:line and a concrete
> interleaving that breaks. End your response with exactly one line:
> `VERDICT: APPROVE` or `VERDICT: BLOCK: <one-sentence reason>`.

**Reviewer 2 — spec conformance against ledgers:**
> Review this diff for conformance against the canonical design-substrate and this workspace's
> ledgers only — do not do a general code review. Diff: `gh pr diff <PR#>` on branch
> `<branch>`. Check: (a) does the diff cite a spec/plan version, and does that version exist
> and say what's claimed — read the actual file, don't trust the cite; (b) does it silently
> extend H_T design at Phase-7 execution time (X-AL-3) — i.e. does it introduce a new
> primitive/contract not already in a cleared spec; (c) does it match the disposition already
> recorded in `.harness/substitutions.yaml`, `.harness/arc-ledger.yaml`, or
> `.harness/forward-register.yaml`, or does it silently diverge from a recorded row; (d) grep
> sibling per-axis specs/plans for a stale cite-shape this diff should have updated too. For
> each concern found, cite file:line + the exact ledger/spec line it conflicts with. End your
> response with exactly one line: `VERDICT: APPROVE` or `VERDICT: BLOCK: <one-sentence
> reason>`.

**Reviewer 3 — test-witness adequacy:**
> Review this diff's tests for witness adequacy only — do not do a general code review. Diff:
> `gh pr diff <PR#>` on branch `<branch>`. For each new or changed test: (a) does it exercise
> the real path a consumer/production entry point would take, or is it a half-proof against an
> isolated seam that the real path never reaches; (b) reason through a mutation probe WITHOUT
> actually editing the tree — if the load-bearing line this test claims to pin were deleted or
> inverted, would the test actually fail, or would it stay green regardless; (c) is the
> verification shape matched to the claim — an e2e/integration check for behavior-over-time
> claims, not just a grep/presence check standing in for one. You are read-only: reason about
> the mutation, do not perform it. For each gap found, cite file:line + what mutation would
> slip through undetected. End your response with exactly one line: `VERDICT: APPROVE` or
> `VERDICT: BLOCK: <one-sentence reason>`.

## Parsing — fail closed

A raw `Agent` fan-out cannot enforce an output schema (that's what the `Workflow` tool's
`schema` option is for, not used here) — the parse discipline below is the only guard:

- The verdict is valid **only** if the response ends with exactly one line matching
  `VERDICT: APPROVE` or `VERDICT: BLOCK: <reason>`.
- **Missing, malformed, or ambiguous → treat as `BLOCK: unparseable verdict`.** Never read a
  silent/truncated/off-format response as approval — this is the same silent-failure trap
  documented for Codex's non-interactive streaming-capture limitation
  (`[[codex-out-of-family-reviewer]]`); it applies just as much to a raw subagent reply.

## Gate outcome

- **All three `APPROVE`** → proceed to merge without HIL (consistent with the standing
  `[[feedback-merge-without-hil-once-ci-green]]` directive — CI-green is a precondition, this
  gate is now an additional one for code-touching PRs).
- **Any `BLOCK`, or a split verdict** → do **not** merge. If the block names a concrete,
  narrow, fixable defect: fix it, then re-run `just codex-review` to convergence and re-run
  this gate. **Cap this at 2 rounds total** — a third disagreement is a genuine decision point,
  not a bug to keep iterating on; auto-fix-and-re-gate without a cap is an infinite loop in
  autonomous mode.
- After the cap, or immediately for a judgment-call disagreement (not a mechanical defect):
  surface via **one batched `AskUserQuestion`** showing all three verdicts verbatim and which
  ones disagreed. Let the operator decide — this is a real fork per §12.4.1, not routine
  progress to auto-resolve.
- **Always report the three verdicts**, even on a clean all-approve — append one row to
  `.harness/merge-gate-log.md` (`PR#`, date, branch, three verdicts, outcome) so "report where
  they disagreed" is auditable after the fact, not just stated in the turn's response.

## Wiring into `ship-pr` / the loop

`ship-pr/SKILL.md` invokes this skill in its pre-merge section — after CI green is confirmed
and `just codex-review` has converged, before the actual `gh pr merge`. `roadmap-continue` →
`ship-pr` is the loop path this composes into; no changes needed to `loop-start`/`loop-stop`
(the gate is a step inside `ship-pr`, not a separate autonomy tier).
