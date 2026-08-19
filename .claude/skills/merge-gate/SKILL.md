---
name: merge-gate
description: Decorrelated 3-lens pre-merge review gate — launches three parallel Agent-tool subagents (concurrency/race-conditions, spec-conformance-against-ledgers, test-witness-adequacy) against a PR's diff, each returning a structured APPROVE/BLOCK verdict. Use right after CI is confirmed green and `just codex-review` has converged, before running `gh pr merge`, for any code-touching PR in the /loop continue → ship-pr flow. Do NOT use on doc-only or `ops: roadmap status refresh` PRs — skip those entirely; the gate only fires when the diff touches `harness-*/src|tests` (or equivalent code surface). Merge only when all three verdicts are APPROVE; any BLOCK or split verdict halts the merge and surfaces the disagreement via AskUserQuestion.
---

# merge-gate — decorrelated 3-lens pre-merge review

An **addition** to the existing pre-merge apparatus (`just review-with-failover` — the fail-closed
`codex-review` wrapper with the `gemini-review` failover — + `advisor()`), not a
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

## Pre-flight — blast radius (run BEFORE launching the reviewers)

A recurring defect class here is not "the changed code is wrong" but **"the change was
right and a consumer of it was missed"** — `[[unconditional-precondition-tightening-ripples-broadly]]`
(B-65-A: grep ALL constructors of the now-illegal shape),
`[[soft-budget-must-never-gate-a-hard-path]]` (grep every consumer on demotion),
`[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`. Each reviewer below sees only
what you write into its prompt, so a consumer nobody enumerated is a consumer no lens checks.

Enumerate it mechanically instead of from memory:

```bash
gh pr diff <PR#> --name-only                 # changed files
graft skeleton <changed-file>                # symbols + spans in each (~200 tok/file)
graft callers <symbol> --depth 2             # who reaches it, annotated by depth
```

Read `--depth 2` output for the **production** consumers — the listing is usually dominated
by test callers, which are not the blast radius. For a rename, signature change, or
precondition tightening, use `--depth all` instead: it surfaces the sibling and downstream
files a single-file edit misses.

Then **paste the resulting consumer list verbatim into Reviewers 1 and 2** (see the prompt
inserts below). Naming the consumers is the point; a reviewer told "check for missed
consumers" without the list just re-derives it worse.

**Fail posture — this is not optional and must not be silently skipped.** The graph lives at
`graft/.graph/wiring.json`, which is gitignored and per-checkout, so a fresh worktree may not
have one. If `graft` is absent or the graph is unbuilt, run `graft build` (it is `$0`,
deterministic, no key, and takes seconds). If it still cannot run, **say so explicitly in the
gate outcome and in the log row** — record `blast-radius: NOT RUN (<reason>)`. A pre-flight
that quietly did nothing reads downstream as a pre-flight that found nothing, which is the
`[[gate-cannot-tell-empty-from-unlooked]]` failure this gate exists to avoid.

**Known limits — state them alongside the list, don't imply completeness.** These are static
call edges: they do not model reference-passing (a callback registered rather than invoked),
`getattr`, string-keyed registries, or plugin loaders. The list is a floor on the blast
radius, never a ceiling. `tools/graft_reachability.py` documents this same limit in detail.

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
> double-fire on a changed step_id. These call sites reach the changed symbols — check each
> for the above, and treat the list as a floor, not a complete set (static call edges miss
> reference-passing, `getattr`, and string-keyed registries): `<paste blast-radius list>`.
> For each concern found, cite file:line and a concrete
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
> sibling per-axis specs/plans for a stale cite-shape this diff should have updated too;
> (e) these files consume the changed symbols — for each, check whether it encodes an
> assumption this diff invalidates (a cardinality, an enum arm, a precondition, a count in a
> docstring or spec table) and was not updated: `<paste blast-radius list>`. That list is a
> floor, not a complete set. For
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
  narrow, fixable defect: fix it, then re-run `just review-with-failover` to convergence and re-run
  this gate. **Cap this at ten rounds total** (operator decision, 2026-08-01) — an eleventh
  substantive disagreement is a genuine decision point,
  not a bug to keep iterating on; auto-fix-and-re-gate without a cap is an infinite loop in
  autonomous mode.
- After the cap, or immediately for a judgment-call disagreement (not a mechanical defect):
  surface via **one batched `AskUserQuestion`** showing all three verdicts verbatim and which
  ones disagreed. Let the operator decide — this is a real fork per §12.4.1, not routine
  progress to auto-resolve.
- **Always report the three verdicts**, even on a clean all-approve — append one row to
  `.harness/merge-gate-log.md` (`PR#`, date, branch, three verdicts, outcome, plus
  `blast-radius: <n consumers>` or `blast-radius: NOT RUN (<reason>)`) so "report where
  they disagreed" is auditable after the fact, not just stated in the turn's response. The
  blast-radius field is logged even when it is `NOT RUN`: a missing field and a field
  recording that the pre-flight could not run are different facts, and only one of them is
  recoverable later.

## Wiring into `ship-pr` / the loop

`ship-pr/SKILL.md` invokes this skill in its pre-merge section — after CI green is confirmed
and `just review-with-failover` has converged, before the actual `gh pr merge`. `roadmap-continue` →
`ship-pr` is the loop path this composes into; no changes needed to `loop-start`/`loop-stop`
(the gate is a step inside `ship-pr`, not a separate autonomy tier).
