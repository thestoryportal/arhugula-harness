# Discipline digest — distilled from Claude-side memory (2026-08-01)

Runner-agnostic distillation of the operative disciplines that live in Claude's memory store and are NOT already carried by CLAUDE.md/AGENTS.md prose. Read at session start alongside `AGENTS.md`. Each entry earned its place by catching (or causing) a real defect in this workspace.

## Verification shapes

- **Two-halves-of-one-mechanism.** A wired handler/field can be UNREACHABLE: unit-green on one half proves nothing until the REAL production path reaches it. The capture side and the read side each need their own witness; a round-trip through the real factory/entry-point is the closer. (Caught at PR #1171: tenant wiring had zero capture-side witness; `tenant_id=None` passed ~107 tests.)
- **Premise-venue tracing.** When a register row / finding names a RUNTIME CONDITION (what blocks what, what races what), grounding must trace the real call chain to the venue — on WHICH loop/thread/process does it occur at a shipped call site? Cites resolving is presence, not premise. (B-103 was BUILT before lens 1 found the loop it rescued does not exist in production.)
- **Mutation-probe witness (PD-8).** Green-alone ≠ proof. Revert the fix, confirm the test FAILS, restore. For matrices: derive the mutation set programmatically; every mutation must produce exactly one named failure; hunt vacuous probes (a probe that passes against the mutant is worse than none).
- **Grep proves presence; only execution proves behavior.** For transit claims, e2e through the real path, asserting the load-bearing surface. Races are non-deterministic — assert lock identity instead of timing.
- **Untested hypothesis ≠ finding.** Reasoning about a scenario the existing repro never exercises is a hypothesis until something runs it, however well-argued.
- **Observation layer before defect.** "No entries / empty / didn't happen" is not a bug until you've confirmed the sink and run a positive control.
- **Count claims drift every review round.** Recount programmatically after EVERY round (variants/shapes/carriers/ACs/rows); grep variant phrasings of the same count.

## Review-loop hygiene

- **Reviewer oscillation → register-and-hold.** 3+ flips on the same point = stop fix-looping; file/hold the sub-decision with the move history.
- **Self-referential loop discriminator.** When a round's findings shift from substance to correction-narration, stop; trim to one line.
- **Convergence ≠ completeness.** Reviewer-quiet is not proof; enumerate the identity dimensions and argue the rest irrelevant explicitly.
- **Non-convergent hardening arms race.** Ask Q1–Q4 "did my fix cause this finding?" and Q5 "does it invalidate the carrier's premise?" — if Q5, STOP and re-scope rather than chase.
- **Reviewer's "systemic gap" framing may be wrong-scoped.** Grep one sibling before accepting a systemic claim; also check whether a later same-PR commit already fixed a BLOCK's citation.
- **Over-correction check.** After 3+ re-corrections of the same passage, diff against round-0 — the original was often already close.
- **Deferred-mechanism spec legs exit on SOUNDNESS** (PD-9), not review-quiet; enumeration coverage capped via a review-time inventory note binding unlisted surfaces BY RULE. Contract-shape findings still reopen.

## Spec/register discipline

- **A spec leg cannot mint a C-\* contract number** (gates require implementing code) — extend an existing contract.
- **Stale-as-described sweep.** When amending any spec, grep SIBLING specs/plans for sentences the amendment falsifies — the workspace's biggest defect class.
- **Closed-schema omission is a contract decision**: ENFORCED → fix-now; advisory → register. Detect-then-refuse needs a witness in BOTH directions.
- **Register prose blocks are REPLACED, not appended** — a `--detail` lookup must never return a pre-ratification story. Superseded reopening rules are struck in place `[SUPERSEDED <date>]`, not deleted.
- **Unconditional precondition tightening ripples**: grep ALL constructors of the newly-illegal shape before landing.
- **Cross-axis type in one axis package = import-cycle defect**; re-home to harness-core/runtime. OD→CP is the canonical direction; harness-cp must not import harness-od.
- **New surface audit**: does the workspace_state/identity hash capture the new dimension; carrier choice = config / by-ref / hash-inert / DROP-when-empty.

## Git/CI mechanics (this repo)

- **NEVER `git add -A`** — stage explicit paths (a `-A` once leaked 327 untracked files to main).
- **Refresh must be the immediate next commit after a substantive merge** (a non-refresh follow-up hard-fails the CI drift check). Merge-gate log row lands BEFORE the merge; refresh right after.
- **Squash-merge branch prune** via `gh pr list --state merged` head-ref cross-ref, never `--is-ancestor`.
- **`main` history floor is 2026-07-25** (whole-tree re-add at d45ce125): per-file `git log`/`merge-base`/`--since` before it silently misfire.
- **rtk wrapper hazards**: it rewrites grep→rg (escaping/paren breakage) and its test summary mislabels xfail as failed — verify with `grep -c FAILED` or `rtk proxy`. `just` variadic `*ARGS` loses quoting on `#`/spaces — call scripts directly.
- **uv workspace**: `uv sync --all-packages` (plain sync misses members). New `HARNESS_*` scalar needs BOTH `_ENV_SCALAR_FIELDS` and `_RuntimeEnvSettings`.
- **CI is ~75s** — poll once at ~80s. Benign non-zero exits (pending checks, no-match greps) are not failures.

## Async/process gotchas (hard-won)

- `asyncio.timeout`: deadline = CancelledError INSIDE the block, TimeoutError only outside; an inner-coro TimeoutError is a branch error.
- `fork()` after acquiring a `threading.Lock` hangs the child — fork BEFORE, gate via Event.
- All production pause-snapshot captures run under `_run_protocol_method_sync` → `asyncio.run` on a private single-task loop in a `to_thread` worker — there is no main-loop to starve (the B-103 lesson).
- Process-lifetime adoption vs irreversible instance state: check for a one-way teardown flag first.
- YAML plain scalars: space+`#` truncates as a comment — splice with single-quote escaping, never re-dump the whole file.

## Operator interaction (unchanged under any runner)

- Labels like operator-gated/DEFERRED mean "drive to the genuine gate, then ask" — never park. A ratified HELD row is a real answer; honor it.
- Surface gates batched + minimal: real architecture forks, credentials, paid calls, irreversible/outward actions. Default to doing + reporting.
- No unilateral paid provider calls or secret relocation; build to the boundary and log it (`just codex-credential-gate`).
- Adjudicate technical disputes via decorrelated reviewers + witnesses, not the (non-coding) operator; gate only on findings that change a committed decision.
