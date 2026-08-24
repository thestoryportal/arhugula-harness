---
name: defect-class-preflight
description: Pre-commit self-review sweep against the ten defect classes this workspace's reviewers actually catch, distilled from the workspace's merge-gate/codex finding corpus (1,084 findings at first distillation, 2026-08-24; the log only grows and scripts/refresh-classes.py rederives). Use BEFORE every commit of code in an arc — after writing or modifying any code under tools/ or harness-*/ and before invoking `just review-with-failover` or the merge-gate. Also use whenever about to claim a fix is complete, whenever a diff touches a shared surface (env variables, hooks, conftest, constants), and whenever a review round's fix is being committed (fixes introduce their own defects at a measured rate). Running this sweep is how a first draft survives review instead of generating BLOCK rounds — skipping it is how arcs run 9–17 review rounds.
---

# defect-class-preflight — sweep the diff before the reviewers do

## Why this exists

This workspace's review loop is fail-closed: every defect a reviewer finds costs a full
serial cycle (fix → probe → commit → CI → re-review → re-bind), typically 15–30 minutes.
Analysis of the recorded findings in `.harness/merge-gate-log.jsonl` (1,084 at first distillation, 2026-08-24; the committed corpus below is newer) shows they
cluster into ten recurring classes — and repeatedly, the defect found was a shape the
workspace had *already fixed once elsewhere* (the same two-armed restore shipped twice in
one arc). The knowledge exists; this skill is its activation at authoring time. One pass
here converts review rounds into pre-commit edits.

## How to run the sweep

Scope it to the diff, not the repo: `git diff HEAD` (or `--cached`) plus any new files.
**Step one, always: run `scripts/preflight-grep.sh`** — it flags high-signal textual
shapes, and every hit demands a NAMED answer in your sweep (its silence proves nothing;
it exists because instruction-following alone measurably misses shapes the grep cannot:
the two-armed save/restore was named in only 1 of 4 skill-eval reviews until it was
mechanized). Then, for each changed hunk, walk the classes below **in order** — they
are ranked by real finding frequency — and answer each applicable class's question
concretely (name the line, not "looks fine").

Two meta-rules that outrank the list:

- **A fix you just wrote is the least-reviewed code in the arc.** After absorbing a
  review finding, sweep the fix itself with this list before committing — measured
  across recent arcs, roughly a third of findings were introduced by a previous round's
  fix.
- **Touching a shared surface obligates a blast-radius pass first**: `graft callers
  <symbol> --depth 2` (or `--depth all` for renames/precondition changes) plus a grep
  for every consumer, then read each consumer's *semantics*, not just its existence.
  The costliest P1 in the corpus was a variable that named TWO authorities — the
  change was correct for one consumer class and destructive for the other.

## The ten classes, ranked by finding count

*(Counts and order regenerated from the committed log by `scripts/refresh-classes.py` at the 2026-08-24 committed corpus of 1,095 findings — rerun the script for live figures; the log only grows, so these are a bound snapshot, not live state.)*

### 1. Race / TOCTOU / atomicity (379 findings)
Any check-then-act on files, refs, locks, or shared state. Ask: *between my check and my
act, what can another lane, process, or signal do?* Shapes: absence-check then create
(use exclusive create); read-modify-write without CAS; cleanup racing a writer;
`mkdir` without `exist_ok` semantics thought through; rename/unlink where a crash
mid-sequence leaves a half-state. This workspace's idioms: exclusive-create CAS
(reservations), temp-then-`os.link` publication, single-writer leases. If your diff
adds coordination, name which existing idiom it uses — a new hand-rolled one is a
finding waiting to be filed.

### 2. Prose that will drift (151 findings)
Docstrings, comments, and `.harness` prose containing checkable facts: counts, line
numbers, §-cites, "all/every/only" absolutes, arithmetic that implies a partition.
Rule: a fact checkable against HEAD does not belong in prose unless bound to a commit
or a round ("six witnesses" was wrong twice in one arc; the census "6288+82" implied a
false partition). Fix at authoring: delete the count, bind the claim, or verify the
cite by reading the cited section *now*. (Full discipline: the `register-pr-prose`
skill.)

### 3. Silent failure / meaning-changing fallback (114 findings)
`2>/dev/null`, `|| true`, `except: pass`, a default that changes meaning when the
primary path fails, an empty result indistinguishable from "could not look". Ask of
every error path: *if this fails at 3 a.m., does anyone find out, and does "empty"
mean empty or unlooked?* A gate that can't tell those apart must fail loud.

### 4. Vacuous witness (107 findings)
For every new/changed test, reason the mutation through before committing: *if the
load-bearing line were deleted or inverted, does this test actually red?* Traps seen
repeatedly: presence-check standing in for behavior (asserting a variable is set, not
that the writer honors it); a witness that dies before reaching its discriminating
assertion (KeyError before the emit); a child process that never instantiates the
thing under test; an assertion after an early return. Where feasible, actually run the
mutation probe (`just mutation-probe`) rather than reasoning it — and probe the fix
BOTH ways (kill confirmed, then green restored).

### 5. Timeout / retry / budget arithmetic (93 findings)
Any bound, retry, or budget: sum the worst case and compare against every enclosing
bound (three retry budgets inside a 30 s waiter summed to 33.9 s). Unvalidated
environment-sourced budgets, wall-clock assertions that breach under load (assert the
SHAPE — call counts — not the milliseconds), sleeps standing in for synchronization.

### 6. Unreachable / dead branch (75 findings)
Every `else`, `except`, and restore arm: *what call sequence reaches this?* The
recurring shape: a hand-rolled two-armed save/restore where one arm is unreachable
from any real caller. It hides in EVERY syntax — an `if saved is None: pop / else:
set` pair reads the same whether it sits in a bare function, a `finally:` block, a
context manager's exit, or a fixture's post-`yield` tail; sweep every save/restore
PAIR by its shape, not by where it appears (an eval reviewer holding this very
checklist walked past one wrapped in `try/finally`). Preferred fix is deletion via a
mechanism that owns both modes (`MonkeyPatch`, a context manager) — delete the branch
rather than contriving a witness for it.

### 7. Env-var mutation and restore (73 findings)
Any `os.environ` write: who restores it, does the restore survive a mid-test
`monkeypatch.undo()` (use an INDEPENDENT `MonkeyPatch`), does it leak into suites that
assert the namespace empty (`HARNESS_*` must never escape tools items), and — the P1
shape — does the variable serve MORE THAN ONE consumer meaning? Enumerate every reader
of the variable before repurposing it.

### 8. Subprocess boundary (58 findings)
Monkeypatching a Python seam cannot reach a child process — only inherited env can.
Children get a COPY of env at spawn; later parent changes don't propagate. Nested
sessions of the same tool (pytest-in-pytest) re-run your own hooks against
already-modified state — first-writer-wins any value that must survive nesting.

### 9. Path / default resolution (56 findings)
Any path computed from env-or-default: TRACE the chain to the concrete path it lands
on when NOTHING is set, and write that path into your review — "falls back to
`~/.reports/` (the operator's real store) when the env var is unset" is a *named
finding*, not an implementation default to read past. Def-time constants bake the env
at import (`QUEUE_DIR`) — a later env change does not reach them. A worktree does NOT
isolate `$HOME`-absolute paths; isolate by ENVIRONMENT.

### 10. Fixture scope / lifecycle phase (35 findings, but two P1s)
pytest specifics that shipped defects: a per-item bracket covers setup+call+teardown
but NOT collection/import time or session-fixture teardown after a foreign final item;
higher-scope teardown runs inside the CURRENT item's teardown phase (measured);
`conftest` runtest hooks fire for items ANYWHERE in the run unless path-guarded; a
function-scoped autouse fixture covers only the test body.

## When a reviewer catches what this sweep missed — the skill's own repair loop

This checklist is a distilled map of `.harness/merge-gate-log.jsonl`; the log is the
authority and only grows. Passive knowledge decays (a rule recorded in memory failed
to prevent the same defect days later, in the same arc that wrote it), so the repair
obligation is IN-COMMIT, not remembered:

When absorbing any reviewer finding this sweep should have caught, classify the miss
and repair the skill **in the same absorption commit**:

- **Absent** — no class covers it → add the class (or extend one), with its question
  and the real example.
- **Unfired** — the class exists but its wording didn't trigger on this shape → rewrite
  the item so the shape is unmistakable (class 6's `finally:` note exists because of
  exactly such a miss).
- **Overridden** — the sweep flagged it and the flag was argued past → the text is
  fine; record the override in the arc's register instead, and consider promoting the
  class DOWN the activation ladder (into `scripts/preflight-grep.sh`, a ruff/semgrep
  rule, or a CI check) — mechanical firing beats instruction-following for classes
  that recur despite being written down.

Then add the miss as a planted-defect case in the skill's eval set
(`evals/evals.json` in this skill's directory), so the repair is
regression-tested like code. The skill file is tracked; its git history is the audit
trail — no separate ledger.

**Staleness check:** `scripts/refresh-classes.py` re-clusters the live gate log and
prints per-class counts plus recent findings matching NO known class — those
unmatched findings are new-class candidates. Run it when the log has grown
meaningfully since the counts in this file (the class headings are bound to the
corpus named above them).

## Exit condition

The sweep is done when every applicable class has a named answer for the diff — not
"checked, fine" but "class 7: the only env write is X at line N, restored by the
stashed MonkeyPatch at M, sole consumer verified via grep". Findings you choose not to
fix now must be named in the commit message or register, never silently carried. Then
commit and invoke the reviewers — they should be confirming, not discovering.
