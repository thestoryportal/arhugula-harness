---
name: defect-class-preflight
description: Pre-commit self-review sweep against the ten defect classes this workspace's reviewers actually catch, distilled from the merge-gate/codex finding corpus (the corpus only grows; scripts/refresh-classes.py rederives counts). Use BEFORE every commit of code in an arc — after writing or modifying any code under tools/ or harness-*/ and before invoking `just review-with-failover` or the merge-gate. Also use whenever about to claim a fix is complete, whenever a diff touches a shared surface (env variables, hooks, conftest, constants), whenever a review round's fix is being committed (fixes introduce their own defects), and whenever a diff introduces a new consumer of an existing data surface — another tool's log/ledger/store/output, an env variable, or an external SDK — which fires the new-consumer inventory pause at authoring time, BEFORE the consumer is written. One pass here is how a first draft survives review — skipping it is how arcs run 9–17 BLOCK rounds.
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

## The new-consumer inventory pause (authoring-time — fires BEFORE the sweep)

Everything else in this file runs at pre-commit. This section runs earlier: the
moment you are ABOUT to write code that reads a data surface some other code owns.
Trigger: the diff introduces a NEW consumer of an EXISTING data surface — another
tool's log, ledger, store, or output file (`.harness/merge-gate-log.jsonl`,
`.harness/substitutions.yaml`, reservation records), an env variable someone else
writes, a JSON/YAML schema owned elsewhere, or an external library/SDK's API. When
that trigger fires: STOP. Do not author the consumer yet.

Why the pause pays: in one recent arc, roughly 13 of the first 20 reviewer findings
were serially-discovered producer contracts — "that field can be null," "absent on
legacy rows," "the writer can die mid-record" — each surfaced one at a time, each
costing the same full serial cycle "Why this exists" prices at 15–30 minutes. One
up-front inventory table would have converted all of them into pre-commit edits.
Letting reviewers read the producer to you, one field per round, is the most
expensive possible way to read it.

The rationalization you will hear yourself think, mid-arc, is: *"the field obviously
exists — I'll just read it."* Treat that exact sentence as the tripwire, not a
waiver. Every one of those ~13 findings was a field that obviously existed; what did
not obviously exist was its null case, its absent-on-old-rows case, its
half-written-at-crash case, its provenance. The field name is the visible tenth of
the contract — the pause exists to surface the other nine tenths before a reviewer
does.

**The inventory.** For EVERY field the consumer will read, establish the producer's
semantics — not the schema you assume, the semantics the writers actually implement:
can it be null? absent entirely (older rows, optional emit paths)? partially
written — what does a mid-crash write leave on disk? what provenance / generation /
versioning does it carry, and must the consumer honor it? which `C-*` contract (if
any) governs it? Two dimensions field-level inventories measurably miss (u-he-33,
2 P1s): **venue semantics** — which interpreters/venues can IMPORT or reach the
producer module at all (a 3.12-only producer consumed from a stdlib-3.9 venue
silently no-ops every downstream check), and **lifecycle semantics** — where the
data goes when its carrier ends (a lease's `unblocked_from` had to be found again
in the moved-aside `released.*` records after release; the live object is not the
record's whole life). Instruments: `graft callers` / `graft grep` on the producer symbol
to read every WRITER's semantics — the meta-rule's blast-radius pass, pointed the
other way — and `just overlay-query` for the `C-*`/`U-*` contract cites. Record the
answers in a TABLE, field × semantics. That table IS the test matrix — and the unit
is the recorded SEMANTIC, not the row: each field × each recorded semantic (null,
absent, partial, provenance, …) is its own case the consumer must survive, and
testing one variant does not retire the field's others. A recorded semantic without
a test is a reviewer finding on layaway.

**Parse, don't validate.** A data-surface consumer gets a typed row model — Pydantic
v2 in this workspace — at the boundary; illegal shapes are rejected ONCE, at parse
time, and everything downstream handles only legal ones. The shape to refuse:
`dict.get()` chains scattered through the logic, each one a private, unreviewed
theory of the producer's contract. Ten `get()` sites are ten places the theory can
be wrong; one row model is one.

**Precedent search.** Before writing the new consumer, read how the surface's OWN
tooling already handles these fields — its existing consumers, the producer's own
reader. The precedent usually already answers the null/absent/partial questions
(someone paid for those answers in review rounds once). Match it, or name in the
diff why you diverge — a silent divergence from the surface's own reader is a
finding either way.

**External-SDK half.** When the consumed surface is an external library/SDK rather
than an in-repo file, the same pause applies, with a three-rung ladder:

1. **Run the interface** — actually call the API/CLI and look at REAL output.
   MANDATORY wherever a read-only, free probe exists, and never replaced by any
   rung below: every `resp["items"][0]` written unprobed is a checkable claim
   about a shape you have not seen. When the only available probe would be paid,
   credential-gated, or mutating, do NOT fire it — the standing
   no-unilateral-paid-calls rule wins: complete the pause on the remaining rungs
   plus the producer-source read, record the unprobed shape as a NAMED gap in the
   inventory table, and surface the probe itself to the operator gate.
2. **Read the resolved installed source** — the zero-cost middle option. FIRST
   resolve what actually runs — the real import path/executable and its version
   (`python -c "import x; print(x.__file__, x.__version__)"`, `which <cli>` plus
   `--version`, or the environment's own metadata) — THEN read that source. The
   repository `.venv` is the common landing spot, never an assumption: a stale
   `.venv` beside a `uv run --with` environment, a system package, a Node SDK, or
   a global CLI all read fine and inventory the wrong producer — source read at
   the wrong version is a wrong-contract inventory wearing the right one's
   clothes.
3. **context7 MCP** for current upstream docs — configured in the workspace
   `.mcp.json`; its tools are deferred, so load them via ToolSearch before
   calling. In a runner without context7 (the Codex bridge, say) the pause
   completes on rungs 1–2 — this rung is an accelerator, never a dependency.
   context7 supplements the probe, never substitutes for it: a probe witnesses
   ONE instance, so it falsifies a doc claim only for the shape it actually
   received — a doc- or source-derived variant the probe did not witness STAYS
   in the inventory table as a case to handle; the probe narrows nothing it did
   not see.

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
finding waiting to be filed. And any file a privileged or auto-allowed path READS or
WRITES that another actor can pre-plant gets the containment idiom: open with
`O_NOFOLLOW|O_NONBLOCK` + post-open `fstat` `S_ISREG`, refuse symlinks/special files
loudly, publish via same-directory temp + `os.replace` (the finding_record/merge_door
hardening; missed unfired on the B-215 gate's state file, codex r1).

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
mean empty or unlooked?* A gate that can't tell those apart must fail loud. The
shape that got past this wording for THREE consecutive review rounds (u-he-33): a
helper whose `except`/error arm returns the success-shaped empty (`return []`,
`return None`, `return set()`) — every one of those is this class wearing a return
statement; route the failure to ONE loud enforcement point instead. Rider for
DETECTION/ENFORCEMENT surfaces: any input that can SUPPRESS a check (an attestation
set, an exemption list, an allowlist, a dedupe key) is itself attack surface —
sweep it for forgeability and containment (symlinked dirs/files, schema-shaped
forged entries) before trusting it to mute anything.

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

## After every review round — the class-sibling sweep (before the next invocation)

A reviewer finding names an INSTANCE; the absorption owes the CLASS. Measured on the
u-he-33 arc: the returns-empty-on-exception shape was found in one helper in round 2
and then re-found in two sibling helpers across rounds 4-5 — two full rounds spent
re-discovering a class already in hand. So, after adjudicating a round's findings and
BEFORE re-invoking the reviewer:

1. Classify each finding into the classes below (or the pause's dimensions).
2. Sweep the ENTIRE diff for other instances of that class — grep the shape
   (`except`, `return []`/`return None` on error arms, the suppression inputs, the
   bare counts), then read each hit's semantics. Fix siblings in the SAME absorption
   commit; the reviewer should never meet the same class twice in one arc.
3. Adjudicate each absorbed finding on the gate log (C-HE-24 §5, U-HE-47): for every
   finding row this round produced, once its fix is committed (or it is refuted with
   grounds), append the disposition — `just merge-gate-adjudicate --finding-id <id>
   --disposition accepted|rejected --actor <runner>_absorber` (`accepted` = the fix
   was applied; `rejected` = refuted; the finding_id is on the round's emitted JSONL
   rows). The actor is the RUNNER's own absorber identity — `claude_absorber` on the
   Claude runner, `codex_absorber` on the Codex bridge — never the producer, never
   `operator`. Without this row the finding stays disposition=null forever and N6 counts
   nothing — the attest below records that you ANSWERED the finding, never that it
   was DISPOSED.
4. If the class was absent/unfired in this file, repair the skill in that commit too
   (the loop below).
5. When two consecutive rounds' findings target mechanisms YOUR absorption invented
   (not the plan floor), stop hardening and re-scope by subtraction — the recorded
   adversarial-hardening arms race does not converge by adding layers.

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
stashed MonkeyPatch at M, sole consumer verified via grep". If the diff introduced a
new data-surface consumer, the inventory table (field × semantics) is part of the
named-answer set — every recorded semantic either tested, or carried as an explicit
deferred finding per the next sentence (sitting in the table is not "named"). Findings you choose not to
fix now must be named in the commit message or register, never silently carried. Then
commit and invoke the reviewers — they should be confirming, not discovering.

Since B-215, the named-answer set is ATTESTED, not merely written: after the final
commit, `HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> just
review-attest-preflight <answers-file>` — the inline prefix is REQUIRED exactly as
for the review itself (the attest verbs resolve the arc via env_arc_and_lane(); a
bare invocation attests the branch-* fallback arc, not the reserved one). The
review wrapper refuses round 1 of a reserved arc without a live attestation
(`tools/review_loop_gate.py`; the attestation binds head+diff, so attest after the
last commit). The "after every review round" sweep ends the same way: absorb,
commit, then the same-prefixed `just review-attest-sweep <answers-file>` naming
every outstanding finding_id (token-exact; obligations span both loop channels and
all rounds).
