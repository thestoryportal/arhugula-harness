---
name: merge-gate
description: Decorrelated 3-lens review — the lens half of the bounded review cycle (spec v1.9 X9a). Launches Agent-tool subagents (concurrency/race-conditions, spec-conformance-against-ledgers, test-witness-adequacy) against a PR's diff, each returning a structured APPROVE/BLOCK verdict recorded per pass with `merge-gate-emit-pass`. Use as soon as the PR is pushed, concurrent with CI, in the /loop continue → ship-pr flow: pass 1 runs all three lenses beside codex, pass 2 the witness lens on the fix delta, the escalation repeats pass 1 at most once, pass 3 is one lens on the full diff. Doc-only PRs run pass 3 alone; skip only `ops: roadmap status refresh` PRs. Merge only when CI is green and pass 3 is clean; pass 3 raising an accepted P1 on two consecutive runs stops the arc and surfaces via AskUserQuestion.
---

# merge-gate — decorrelated 3-lens pre-merge review

The lens half of one bounded review cycle per PR (spec v1.9 X9a, `## The review cycle`
below); the codex half is `just review-cycle-pass` — the fail-closed `codex-review` wrapper
with the `gemini-review` failover — and the §13.1 transcript-brief review stays beside both.
It composes with `ship-pr` — see the wiring note at the end.

## Honesty caveat — read this before trusting an all-approve

The three subagents below are Claude Agent-tool subagents: **lens-decorrelated, not
vendor-decorrelated.** Same model family, same training-time blind spots. Their value is that
each goes *deep on one specialty* the generic pass skips, not that they're independent eyes in
the way Codex (`just codex-review`, out-of-family, $0 subscription) or the
transcript-brief review (the §13.1 transcript-aware half) are. This gate does **not** replace either — it runs alongside them. If a
finding matters and you want real cross-vendor confidence, that's still Codex's job.

This gate is **instruction-level, not a hard hook.** `permission-guard.sh` is a shell script —
it cannot launch subagents. Enforcement here is the loop agent following this documented
procedure, exactly as reliable as that compliance. It is not a mechanical block the way the
deny-list is.

## Scope gate — which cycle a PR runs

Before doing anything else, check the PR's changed files (`gh pr diff <PR#> --name-only` or
equivalent). A **terminating refresh PR** (`ops: roadmap status refresh …`, touching only
`.harness/roadmap_status.md`) runs no cycle — **skip this gate entirely.** A **doc-only** PR
runs pass 3 alone: one lens on the full diff, no codex half (X9a). Every other PR — any diff
touching `harness-*/src/**`, `harness-*/tests/**`, or equivalent runtime code (hooks, tools
scripts with real logic) — runs the full cycle. The gate reads the diff itself (`doc_only`)
and refuses a pass out of order, so the scope you infer here is checked, not trusted.

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

## Binding — publish BEFORE launching (C-HE-15 §4, U-HE-13; bindings by file, WR-09)

Each lens verdict is bound to the exact tree it reviewed. For each lens id —
`merge-gate-concurrency`, `merge-gate-spec-conformance`, `merge-gate-witness-adequacy` — run
`just merge-gate-binding <id> <base>` on the checked-out PR head, where `<base>` is the
pass's diff base: `origin/main` for pass 1, the escalation and pass 3 (the full diff), and
the head the previous pass reviewed for pass 2 (the fix delta — the emitter refuses any
other base, `WRONG_BASE`). A lane's local `main` is stale; never bind against it. It writes the six
values (`head_sha`, `base_sha`, `diff_digest`, `reviewer_identity`, `prompt_version`,
`config_hash`) to a file and prints **only that path**. Name the printed path in that lens's
prompt and tell the lens to READ it — never copy a value through this turn. Both round-3 lens
corruptions were orchestrator transcription errors (a truncated `head_sha` → one re-emit; a
spliced `base_sha` → a full 0.38M-IET lens rerun, ≈5 min on the critical path) [B] F3, and a
value you never handle is a value you cannot corrupt. The lens copies the six VERBATIM out of
that file into its fenced JSON block; `emit` (below) recomputes them and refuses a verdict
whose values differ (a moved head, a swapped lens) — the verdict is then NOT recorded and
does not count.

## Prompt authoring — delegate under `laws:prompt`

**Subagent prompts are authored under `laws:prompt` (U-SR-03, charter WR-08).** A subagent
sees only the prompt you write — no transcript, no CLAUDE.md, no user requirement unless you
put it there. Delegate the authoring to an agent that adopts `laws:prompt` and use the prompt
it returns; composing one inline is legal ONLY when instantiating a skill-canonical template
with literal values. A freehand prompt written in a `laws:code` session is the defect this
rule exists to stop: the passive memory (`[[feedback-subagent-prompts-are-laws-prompt-medium]]`)
failed twice in 48h, and delegating costs ~1m13s / 0.11M IET — about 3% of one lens run. The
`agent-prompt-advisory` PreToolUse hook restates this at every `Agent` call; it is advisory
and never denies. The delegate's OWN invocation is the base case: launching the
laws:prompt authoring agent uses the one-line brief `Adopt laws:prompt and author the
subagent prompt described below; return only the finished prompt.` plus the task
description, and needs no further delegation -- without a named base case the rule
recurses forever, since every authoring agent would itself need an authored prompt.

The three reviewer prompts below **are** the skill-canonical template: instantiating them
with this PR's literal values (PR number, branch, blast-radius list, binding-file path) is
the sanctioned inline path. Departing from them — a new lens, a re-worded specialty, an
extra instruction — is authoring, and goes through the delegate.

## The three reviewers — launch a pass's lenses in ONE message, parallel Agent calls

A pass launches only the lenses X9a gives it (pass 1 and the escalation: all three; pass 2:
Reviewer 3; pass 3: one — the lens whose domain is the arc's mechanism, e.g. concurrency
for a race). Commit every fix BEFORE launching, and keep the read-only instruction in each
prompt: a lens once reverted uncommitted fixes in the shared tree.

Each prompt must be **self-contained** (a subagent sees only what you write — no conversation
context) and must include the PR's diff or a pointer to fetch it
(`gh pr diff <PR#>`), the branch name, and the specific lens. Generic "review this PR" prompts
just triplicate what Codex already does — go deep on the specialty, explicitly forbid a
generic pass, and demand a machine-parseable verdict line. **Every prompt also demands, immediately
before the `VERDICT:` line, ONE fenced ```` ```json ```` block matching
`tools/review_schemas/merge-gate.schema.json`: keys `verdict` (APPROVE|BLOCK), `findings`
(array of `{severity: P1|P2|P3, location, message}`, empty on APPROVE, non-empty on BLOCK) and
the six binding values copied verbatim — no other keys.** Append that sentence to each of the
three prompts below, naming the **binding-file path** the recipe printed for that lens and
instructing the lens to read the six values from it; the values themselves never appear in
the prompt you write.

**Every prompt also carries the PROSE-FINDING RULE below, verbatim** — it is what stops a lens
from spending a merge on a wording nit, and a lens that has not been told it will BLOCK on one:

> **Prose findings are P3 and NON-BLOCKING.** A prose finding is one whose whole effect is on
> text a human reads: a count, an ordinal, a superlative or absolute, a wording or
> characterisation, a `file:line`/§ cite that has drifted, a stale comment, a claim about the
> work's own history. Report them — briefly, at the END of your report, under a
> `### Non-blocking prose notes` heading — but they MUST NOT make your verdict `BLOCK`, and a
> report whose findings are ALL prose MUST end `VERDICT: APPROVE`. Put them in the JSON
> `findings` array with `severity: P3` so they are recorded. If a defect changes what the CODE
> DOES, or what a TEST actually witnesses, it is not a prose finding — classify by EFFECT, not
> by which file it lives in, and when genuinely unsure treat it as substantive.

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
> You are read-only: do not edit, stage, stash, reset or check out anything in the tree.
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
> floor, not a complete set. You are read-only: do not edit, stage, stash, reset or check
> out anything in the tree. For
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
- **Record each lens verdict into its pass through the structured sibling (C-HE-23 §2).**
  Write each lens's full response to `.harness/tmp/merge-gate-lens-<id>.txt` (in-worktree,
  gitignored — the permission guard auto-allows the wrapper only on in-worktree paths) and
  record it with
  `HARNESS_LANE_ID=<lane-id> just merge-gate-emit-pass <pass> --pr <PR#> --arc-id <arc-id> --lens <id> --verdict-json .harness/tmp/merge-gate-lens-<id>.txt --base <base>`
  (`<pass>` is `1`, `2`, `esc` or `3`; `<base>` is the same base the lens was bound to above.
  `--arc-id` is the RESERVATION id, e.g. `u-he-34` — omitting it defaults the row's
  `arc_id` to `pr-<N>`, which breaks the join N6, the reservation phase rows and the cycle
  admission key on; U-HE-34 r6. `<lane-id>` is this lane's `.harness/.lane-id` content,
  typed as a literal: a bare call records the `-nolane` fallback in every row's `lane_id`,
  which C-HE-24 §6 requires to name the lane). The emitter admits the verdict into the pass
  through the same admission as the codex half (`_decide_cycle` in
  `tools/review_loop_gate.py`: order, reviewer set, base, adjudication, fix-committed), and a
  refused emit prints its refusal code and the recipe to follow. A lens verdict recorded without its
  pass (the older `merge-gate-emit` / `merge-gate-emit-all` recipes) delivers into no pass
  and cannot complete one. **One verdict per lens per pass:** a lens that exited 2 is
  re-run and recorded alone; a lens that already delivered is refused (`ALREADY_DELIVERED`).
  There is no resumption: the JSONL is the only record, and nothing is skipped on its say-so.
  Until B-295 closes, the schema refuses an `APPROVE` whose `findings` array is non-empty:
  move an approving lens's P3 notes to the arc's follow-up row (`## The review cycle`) and
  empty the array before emitting, or the verdict is not recorded.
  Each lens's record parses the fenced JSON against the schema, holds it to the binding, requires the final
  `VERDICT:` line to agree with it (exact-line match), and writes the
  `.harness/merge-gate-log.jsonl` rows FIRST and a structured `.harness/merge-gate-log.md`
  line second. Exit 0 = APPROVE recorded, 1 = BLOCK recorded, **2 = NOT recorded (no schema
  block / binding mismatch / unwritable JSONL) — the lens verdict does not count; treat as
  BLOCK-equivalent and re-run that lens** (a bound `reviewer_unavailable` marker is written
  when the JSONL is writable). A verdict that was never recorded is not a verdict.

## The review cycle (spec v1.9 X9a; C-HE-21 §1)

Each PR runs **one** bounded cycle, launched the moment the PR is pushed and run concurrently
with CI. It replaced review-to-convergence: the cycle is the bound, and the table below is
the whole of it.

| Pass | Codex half — `review-cycle-pass` | Lens half — `merge-gate-emit-pass` (lane-prefixed, see `## Parsing`) | Diff read |
|---|---|---|---|
| 1 | codex | all three lenses | full (`origin/main`) |
| fix | — | — | adjudicate every finding; fix and commit every accepted P1/P2; push once |
| 2 | codex, base = the head pass 1 reviewed | witness-adequacy | the fix delta |
| esc | codex — only if pass 2 raised an accepted P1, and at most once | all three lenses | full |
| 3 | none | one lens (the arc's mechanism) | full |

**Every accepted finding gets exactly one disposition, whichever pass raised it:**

- An accepted **P1** blocks until fixed. Raised in pass 2 it triggers the escalation; raised
  in the escalation or in pass 3, fix and commit it and pass 3 re-runs.
- An accepted **P2** raised in pass 1, pass 2 or the escalation is fixed before pass 3 runs.
- An accepted P2 first raised **in pass 3**, and every **P3 or prose** finding from any pass,
  goes into ONE follow-up row for the arc in `.harness/forward-register.yaml` — not fixed in
  this PR, never a pass of its own. Write the row with the last fix commit before pass 3.
  What pass 3 itself raises cannot be committed here (the landing delta admits only the
  gate-log files, so a register commit after pass 3 would owe another pass 3): list each such
  finding id in the arc's close-out checkpoint under Remaining Work, and add it to the row —
  creating the row if pass 3 raised the arc's first follow-up finding — in the first commit
  of the arc's next PR. The gate-log rows are its durable source until then; this timing gap
  against X9a is registered as B-298.
- A **rejected** finding carries its cited law and needs nothing further.

Adjudicate every finding (`merge-gate-adjudicate`, below) before launching the next pass; the
gate refuses the launch otherwise (`ADJUDICATION_MISSING`), and refuses a pass whose accepted
P1/P2 fix is not yet committed (`FIX_NOT_COMMITTED`).

Launch mechanics. The defect-class preflight is attested ONCE, before the cycle's first pass —
pass 1, or pass 3 on a doc-only PR (`review-attest-preflight`, see `ship-pr`; the gate refuses
the first pass without it, `PREFLIGHT_MISSING`; X9a names only pass 1, and the doc-only case is
part of B-298); there is no sweep attestation between passes.
The codex log name is `r<N>.log`, N being the arc's next codex round — normally `r1` for
pass 1, `r2` for pass 2 and `r3` for the escalation, but a `REVIEWER_UNAVAILABLE` round takes a
number too and shifts the rest; a wrong name is refused before launch (`ROUND_NAME_MISMATCH`),
and the refusal names the right one. Never run two codex runs of
one pass at once. While a pass is in flight — its codex half or any of its lenses still running — make no edit in this worktree, not even for the next arc: the lenses read consumer files from the local tree, and no binding pins those bytes, so an edit mid-pass silently changes what a verdict was computed against. CI runs remotely and needs no such hold. A doc-only PR runs pass 3 alone. A commit added after the cycle completes
gets exactly one pass 3 (`CYCLE_COMPLETE` names this). Keep a unit near ~300 changed non-test
lines and split it before pass 1 when it runs over: every full-diff pass reads the whole
diff again, so its size is paid on each of them.

**The stop.** Pass 3 raising an accepted P1 on two consecutive runs — its re-run after a P1 fix raised a P1
again, the same one or a new one — stops the arc: the gate refuses further passes
(`BUDGET_EXHAUSTED`; `unfixed_after_pass_3` counts those runs, not finding identity). X9a
words the stop as a P1 still *unfixed* after pass 3; the gate is stricter, and the divergence
is registered as B-298 — follow the gate, since it is what refuses. Surface it with one `AskUserQuestion`.
The recorded answer is either a deliberate extension (`just review-attest-budget <extra> <reason>`, which buys
`<extra>` more pass-3 re-runs, recorded by the operator and never granted by the loop) or register
and defer (`defer.sh` plus a register row). Nothing merges past a known P1.

You will reach the end of this table with something still bothering you: a pass-3 P2 nobody
saw before, or a pass 1 that came back with nine findings. And you will think *"one more
full pass, just to be safe."* That is the moment. The disposition list above, not the
feeling, decides whether review continues: the P2 goes to the follow-up row, the nine are
adjudicated, fixed, and read again as pass 2's fix delta. Late review does find things (PR
#1034 found real defects deep into its run), and the cycle keeps those findings — they ride
the follow-up row onto the next PR instead of holding this one open. Open-ended review cost
U-HE-53 about four hours; on the cycle, U-HE-57 landed in 68 minutes and B-296 in 73, with
every accepted finding real.

## Gate outcome

- **Pass 3 clean** (its lens returns `APPROVE`, or its only findings are the P2/P3 the
  disposition list carries to the follow-up row) and CI green at the final head → proceed to
  merge without HIL (consistent with the standing `[[feedback-merge-without-hil-once-ci-green]]`
  directive — CI-green is a precondition, the cycle is the review one).
- **Prose-only findings never stop a merge and never buy a pass** (operator
  directive, 2026-09-18, durable). If every open finding is prose per the rule above, it
  blocks nothing: record the rows, adjudicate them, and carry them to the arc's one follow-up
  row. Fix one only where the fix is trivially co-located with work already in the diff;
  either way they ride on the NEXT substantive PR, never
  their own pass. This is the standing calibration, not a per-arc judgement call. What priced it: on
  PR #1561 the gate recorded ~90 findings across thirteen rounds, the great majority
  prose-class, while the arc's two real code defects were found during absorption and
  self-probing and were never gate findings at all — so the rounds that cost the most bought
  the least. Re-derive that shape before citing it; the point is the ORDERING, not a count. A lens
  that returns `BLOCK` on a prose-only finding set has mis-applied the rule — record the
  finding, treat the verdict as APPROVE for gating, and say so in the narrative row.
- **Any `BLOCK` naming a substantive finding, or a split verdict, in passes 1, 2 or the
  escalation** → do **not** merge; it is input to the next step of `## The review cycle`
  (the fix round, then the next pass it names), never a reason to re-run the same pass.
  **Absorption adjudication (C-HE-24 §5, U-HE-47):** when a gate `finding` row's
  fix is absorbed (or the finding is refuted), append its disposition —
  `HARNESS_ARC_ID=<arc-id> just merge-gate-adjudicate --finding-id <id> --disposition accepted|rejected --actor claude_absorber`
  (the `HARNESS_ARC_ID=` prefix is REQUIRED for the guard's auto-allow and is
  holder-bound: the CLI refuses an arc this lane's reservation does not hold, and a
  target row from any other arc; the `finding_id` is on the emitted JSONL row;
  `--actor` must differ from the lens producer, write-time enforced; exit 2 = not
  recorded, re-run). Rejected dispositions
  keep a `unique_catch=true` row from counting (C-HE-29 §2).
- **A pass-3 `BLOCK`** blocks only on an accepted P1: fix it, commit, and pass 3 re-runs.
  The escalation rule's one recorded escape is the stop in `## The review cycle` — pass 3
  raising an accepted P1 on two consecutive runs halts the arc until the operator records an extension or a hold, and
  the loop never grants its own (the v1.5 X5 recorded-decision checkpoint survives only as
  this escape).
- At the stop, or immediately for a judgment-call disagreement (not a mechanical defect):
  surface via **one batched `AskUserQuestion`** showing the pass's verdicts verbatim, which
  reviewers disagreed, and the accepted findings still open. Let the operator decide — this
  is a real fork per §12.4.1, not routine progress to auto-resolve.
- **Always report every pass's verdicts**, even on a clean approve — the `emit-pass` calls
  above are the machine record (JSONL first, structured md line second). **A pass's outcome
  is the worst of its RECORDED rows at the reviewed head, never the last exit code you saw**
  — each lens delivers once per pass, and one lens's BLOCK beside two APPROVEs is a split
  verdict, not an approve; `just merge-gate-log-check` is the C-HE-23 §2 consistency
  reducer); additionally append the
  narrative row to `.harness/merge-gate-log.md` (`PR#`, date, branch, pass, verdicts, outcome, plus
  `blast-radius: <n consumers>` or `blast-radius: NOT RUN (<reason>)`) so "report where
  they disagreed" is auditable after the fact, not just stated in the turn's response. The
  blast-radius field is logged even when it is `NOT RUN`: a missing field and a field
  recording that the pre-flight could not run are different facts, and only one of them is
  recoverable later.
- **Commit the gate rows before merging.** The emitted `.harness/merge-gate-log.jsonl` +
  `.harness/merge-gate-log.md` rows are TRACKED records: commit + push them on the PR branch
  (a gate-row-only delta — the same practice as today's narrative row; it never re-opens the
  lens verdicts, which are bound to the reviewed head), wait for CI at that final head, and
  only then merge. A record left as dirty local state is lost with the worktree and is not a
  record (mirror of the Codex carrier's "commit and push the gate-log row before merge").
  **The approvals transfer to that final head ONLY if `just merge-gate-landing-delta
  <reviewed-head>` exits 0** (the reviewed..final diff names nothing but the two gate-log
  files); any other file in that delta is unreviewed change — it gets one pass 3.

## Standing constraints — live carriers, one bounded cycle (C-HE-21, C-HE-35)

Invariants bind by live carriage (C-HE-21 §2), not by an appeal to their number. Each one this
gate leans on names the text that carries it today:

- **#5 is live** (no verdict inferred from absence) in this skill's `## Parsing — fail closed`
  and in `ship-pr`'s `## Pre-merge gate — CI green + decorrelated 3-lens review (before the
  merge door)`.
- **#14 is C-HE-19**: CANCELLED is INCOMPLETE, never green — carried by `ship-pr`'s post-merge
  CI check and by `tools/merge_door.py`.
- **invariant #16 is void**: C-HE-21 §2 found no concurrent-reviewer-cap carrier in `.claude/`,
  `tools/`, `justfile` or CLAUDE.md. It throttles neither lenses nor lanes.

A later appeal to a numbered invariant cites its live carrier the same way, or it does not
bind. One bounded cycle per PR (C-HE-21 §1, v1.9 X9a): no review runs past pass 3 without
a recorded operator decision, and no mechanized check is cited as grounds for skipping a
pass (C-HE-31, v1.9 X9b).
No eval-harness / model-judge as a governance gate (C-HE-21 §4).

Grounding-gate dispositions this gate inherits (C-HE-35):

- **K5 —** structured findings require location, observed evidence, expected contract and a
  reproduction basis (the C-HE-24 shape); admissible alternatives are optional, not mandated.
- **K6 —** dropped: a reviewer never acquires authority to suppress its own finding by
  self-classifying its scope. A lens may record scope metadata; suppression belongs to a second
  decorrelated lens, a deterministic rule, or a logged operator override, and every suppression
  leaves an audit row. Ambiguous scope blocks.
- **K7 —** routing by arc type and finding class is deferred until their predictiveness is
  measured (C-HE-26 §3); shadow mode only, if run at all.
- **K8 —** a blocking post-edit hook is admitted only for fast, deterministic, low-false-positive
  checks at a stable boundary (C-HE-31 §3), not on every intermediate edit.

## Wiring into `ship-pr` / the loop

`ship-pr/SKILL.md` invokes this skill for every pass of the cycle, from the push that opens
the PR until pass 3 is clean, alongside `just review-cycle-pass` and concurrent with CI; the
merge door follows. `roadmap-continue` →
`ship-pr` is the loop path this composes into; no changes needed to `loop-start`/`loop-stop`
(the gate is a step inside `ship-pr`, not a separate autonomy tier).
