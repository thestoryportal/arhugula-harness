---
name: defect-class-preflight
description: Pre-commit self-review sweep against the recurring defect classes this workspace's reviewers actually catch, distilled from the merge-gate/codex finding corpus (the corpus only grows; scripts/refresh-classes.py rederives counts). Use BEFORE every commit of code in an arc — after writing or modifying any code under tools/ or harness-*/ and before invoking `just review-cycle-pass` or the merge-gate. Also use whenever about to claim a fix is complete, whenever a diff touches a shared surface (env variables, hooks, conftest, constants), whenever a review round's fix is being committed (fixes introduce their own defects), and whenever a diff introduces a new consumer of an existing data surface — another tool's log/ledger/store/output, an env variable, or an external SDK — which fires the new-consumer inventory pause at authoring time, BEFORE the consumer is written. One pass here is how a first draft survives review — skipping it is how arcs run 9–17 BLOCK rounds.
---

# defect-class-preflight — sweep the diff before the reviewers do

## Why this exists

This workspace's review loop is fail-closed: every defect a reviewer finds costs a full
serial cycle (fix → probe → commit → CI → re-review → re-bind), typically 15–30 minutes.
Analysis of the recorded findings in `.harness/merge-gate-log.jsonl` (1,084 at first distillation, 2026-08-24; the committed corpus below is newer) shows they
cluster into a small set of recurring classes — and repeatedly, the defect found was a shape the
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

Three meta-rules that outrank the list:

- **A fix you just wrote is the least-reviewed code in the arc.** After absorbing a
  review finding, sweep the fix itself with this list before committing — measured
  across recent arcs, roughly a third of findings were introduced by a previous round's
  fix, and on the u-he-35 arc 8 of 29 findings landed on code its own absorptions had
  added (charter WR-04, [A] §2).
  The place this rule is actually lost is the sweep ANSWERS. You will have spent the
  last hour inside the reviewer's finding; the work will feel like a repair rather
  than a build; and you will write *"no new mechanism"* into the answers file without
  re-reading what you just added. That is the moment. **A commit that adds a mechanism
  can never answer "no new mechanism"** — the u-he-35 r5 sweep answered exactly that
  while introducing `_LiveGroups`, whose race came back as r6's finding one full round
  later. An answers file carried over from the pre-absorption sweep describes the diff
  you MEANT to write, not the one you are committing: re-run
  `scripts/preflight-grep.sh` over the absorption's own bytes and answer from its
  hits. Under the bounded review cycle (spec v1.9 X9a) nothing checks this for you: the
  preflight is attested ONCE, before the cycle's first pass (`ship-pr`'s admission attestation), and no gate asks
  for a fix-round answers file again. The sweep of a fix is now your own discipline
  between passes, and skipping it stays invisible until the next pass bills for it.
- **Every numeric bound names the contract value it derives from.** Any literal in a
  guard, allowlist, validator, or budget — a range, a cap, an arity, a retry count —
  is either traceable to a contract value you can cite, or it is a guess wearing a
  validator's uniform. Put the derivation where the number is, not in the PR body.
  The rationalization sounds like care: *"1 to 99 is obviously reasonable — nothing
  legitimate falls outside it."* Reasonable-looking is the defect. The u-he-35
  guard-reps token took FOUR paid touches — `any` → `1–99` → `1–9` → `5–9` — because
  each bound was invented from how the line read instead of from what the contract
  says, and each invented bound bought exactly one more round in which to invent the
  next (charter WR-05, [A] §3). Nor is a wide bound the safe default it looks like: a
  range that admits values its contract forbids is a gate that claims to enforce and
  does not — class 12's shape with an integer in it. `scripts/preflight-grep.sh`
  mechanizes the argparse half (`type=int`); this rule covers every literal the grep
  cannot see.
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
any) governs it? Evidence read back from a log or cache is bound to the bytes or
implementation that produced it, or it measures something else (u-he-40 codex r3, twice: a
logged probe line range reused after the code moved, a cached replay result reused after the
checker changed; round 4 found two more — replay rows re-measuring history advanced the LIVE
demotion windows, and a digest of the check's own module missed the modules it delegates to; round 7 another — a
logged line range bound to the source bytes but not to the test whose annotation names
those lines). Two dimensions field-level inventories measurably miss (u-he-33,
2 P1s): **venue semantics** — which interpreters/venues can IMPORT or reach the
producer module at all (a 3.12-only producer consumed from a stdlib-3.9 venue
silently no-ops every downstream check), and **lifecycle semantics** — where the
data goes when its carrier ends (a lease's `unblocked_from` had to be found again
in the moved-aside `released.*` records after release; the live object is not the
record's whole life). A third (u-he-40 codex r9): **encoding semantics** — how the producer
serializes and tokenizes what it writes. A writer shell-quoted a test node into a probe log
whose producer and every reader split the command on whitespace, so the quoted node's own
evidence never matched it; match the surface's tokenization, or refuse the inputs it cannot
carry, rather than adding a second decoder beside the one the producer uses. Instruments: `graft callers` / `graft grep` on the producer symbol
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

## The mechanism-precedent search (grounding-time — fires BEFORE the first line of a new tool)

The new-consumer pause above covers DATA surfaces. This step covers MECHANISM
surfaces, and it fires earlier still — at grounding, the moment you can list which
mechanisms the new tool needs (subprocess lifecycle, signal handling, file
publication, verdict parsing, guard wiring) and have written none of them. For
each mechanism on that list:

1. **Read the reviewed sibling that already does it — then adopt its shape or
   import it outright.** At the 2026-08-26 audit [A] the sibling wrappers
   (`run_bounded`/`terminate_bounded`, `agy_review`, the guard-allow commits)
   carried ~90 absorbed findings of reviewer pressure: they are the reviewers'
   standard in executable form, the local bar. Diverge only with the divergence
   named in the diff — a silent divergence from the reviewed sibling is a finding
   either way, same rule as the data-surface precedent search above.
2. **Grep the gate-log corpus for that surface** (`.harness/merge-gate-log.jsonl`):
   *what has this reviewer said about code like this?* The findings absorbed on
   the sibling's own arc are the exact rounds you are otherwise about to re-buy.
3. **Treat the plan skeleton as UNREVIEWED input.** It sketches shape; it never
   grants contract. Where it contradicts a spec phrase or a reviewed sibling, the
   sibling/spec wins and the skeleton is the finding (class 12's plan-over-spec
   deference — both u-he-35 P1s were exactly this).

The price of skipping, measured (charter WR-11, [A]): at least 7 of the u-he-35
arc's 29 findings re-derived — one paid round at a time — disciplines the sibling
wrappers already embodied. The rationalization arrives as *"my tool's case is
different — faster to just write it."* Whether it is different is precisely what
the sibling read establishes; unread, "different" is a guess priced at one review
round per mechanism.

## The classes, ranked by finding count

*(Counts and order for classes 1–10 regenerated from the committed log by `scripts/refresh-classes.py` at the 2026-08-24 committed corpus of 1,095 findings — rerun the script for live figures; the log only grows, so these are a bound snapshot, not live state. Classes past 10 are appended by the arc that paid for them and carry that arc's count, so they are outside the ranking.)*

### 1. Race / TOCTOU / atomicity (379 findings)
Any check-then-act on files, refs, locks, or shared state. Ask: *between my check and my
act, what can another lane, process, or signal do?* Shapes: absence-check then create
(use exclusive create); read-modify-write without CAS; cleanup racing a writer;
`mkdir` without `exist_ok` semantics thought through; rename/unlink where a crash
mid-sequence leaves a half-state. This workspace's idioms: exclusive-create CAS
(reservations), temp-then-`os.link` publication, single-writer leases. If your diff
adds coordination, name which existing idiom it uses — a new hand-rolled one is a
finding waiting to be filed. A state snapshot read OUTSIDE a lock and
applied INSIDE it is the same shape one level up (u-he-40 codex r5: windows computed for
one promotion could demote the next) — re-validate the snapshot's identity under the lock. And any file a privileged or auto-allowed path READS or
WRITES that another actor can pre-plant gets the containment idiom: open with
`O_NOFOLLOW|O_NONBLOCK` + post-open `fstat` `S_ISREG`, refuse symlinks/special files
loudly, publish via same-directory temp + `os.replace` (the finding_record/merge_door
hardening; missed unfired on the B-215 gate's state file, codex r1). Missed a second time on u-he-40
(codex r7 P1): a state writer staged through a PREDICTABLE `<name>.tmp` opened with
`write_text`, which follows a planted symlink — the staging file needs exclusive creation
(`mkstemp`) exactly as much as the target does.

### 2. Prose that will drift (151 findings)
Docstrings, comments, and `.harness` prose containing checkable facts: counts, line
numbers, §-cites, "all/every/only" absolutes, arithmetic that implies a partition.
Rule: a fact checkable against HEAD does not belong in prose unless bound to a commit
or a round ("six witnesses" was wrong twice in one arc; the census "6288+82" implied a
false partition). Fix at authoring: delete the count, bind the claim, or verify the
cite by reading the cited section *now*. (Full discipline: the `register-pr-prose`
skill.)

**Priority, and why this class keeps its rank here anyway** (operator directive, 2026-09-18,
durable). A prose finding at REVIEW time is **P3 and non-blocking** — it never stops a merge
and never buys a re-gate round (see `merge-gate`'s prose-finding rule). Its rank in this table
is by historical finding COUNT, which is now a measure of how much this class used to cost,
not of how much it should. That does NOT demote the sweep: this pass runs at AUTHORING time,
where the fix is free, and the cheapest prose finding is the one never written. The failure
this ordering must not cause is spending an authoring pass polishing a comment while a class-1
race or a class-4 vacuous witness goes unswept — **when time is short, sweep 1, 3, 4 and 12
first and let this one go.** The single highest-value move here remains subtractive: if a
sentence carries a checkable claim it does not need, DELETE the claim rather than verifying
it — a deleted count cannot drift, and a "corrected" one has a measured habit of drawing the
next finding (PR #1561: one sentence drew a finding in three consecutive rounds, each
falsifying the construct the previous fix introduced). The sentence you are reading was itself
caught mid-authoring asserting an unverifiable attribution about that arc; the gate log
falsified it on a positive-controlled query. Sweep your own prose edit before shipping it.

*Vocabulary evaluated and LEFT OUT for this class (2026-09-18):* a record that **contradicts its
own evidence** — a review audit stating counts the gate log's `round_n` refutes, a cleared marker
naming two of the four rows `--open` emits. The shape is class 2's subject and recurred twice in
one arc, but three terms were tried and all three withdrawn: `omits` (+84 rows, rejected before
shipping), `, not <digits>` (matches any numeric contrast — "The API returns 1, not 2."), and
`identifies only` (shipped on a claim of semantic boundedness that proved false — "The sanitizer
identifies only SQL injection…"). Prose DESCRIBING a record is lexically indistinguishable from
prose about the thing the record describes. Sweep it by hand: for every count, status or
completeness claim a record states, which source of truth refutes it, and did you read that
source THIS session?

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
forged entries) before trusting it to mute anything. A substring match on the suppressing
call is forgeable by a comment that merely mentions it (u-he-40 codex r3: a
`# assert_fake_is_subclass(FakeClock, Clock)` comment exempted a double) — parse the file
and require a call that is KNOWN to run. A parsed call is not yet an executed one: the
u-he-40 codex r8 fix still exempted `if False: assert_fake_is_subclass(...)` and a call
inside a helper nobody invokes. Name the statement position that guarantees execution (a
module-level statement runs whenever the file imports) and exempt only that. The same rider
covers the KEY that looks up a check's evidence: a key coarser than the claim it vouches for
lets one piece of evidence answer for several claims (u-he-40 codex r8: annotations keyed by
test node and file, dropping the lines each names, so two stacked annotations both
re-verified the first one's row and the second was never checked). Key evidence by the
claim's full identity. A reuse or cache key is the same rule from the other side: it binds
EVERY input the cached result read, not just the obvious ones (u-he-40 codex r9, one round
after this sentence was written: replay results keyed by commit and checker implementation,
while one check also reads the PR body — mutable, and fetched over a network that can fail —
so an edited body, or one gh could not fetch last time, kept reusing the stale measurement). A sibling shape (u-he-40 codex r2
P1): a subprocess exit code that means the WORLD may now be damaged — a mutation probe's
`3 = restore failure`, a partial-apply code — mapped onto a finding or a warn row. A
finding is a statement ABOUT the tree; that exit code says the tree may no longer be the
one under review, so it must abort the whole run (advisory mode included) with the
subprocess output preserved, never ride the channel an ordinary result rides. Enumerate
the SAFE exits, never the damaging ones: u-he-40 codex r8 found the r2 fix aborting on `3`
while a SIGKILL (a negative returncode, or 137 through a shell) still became an ordinary
"indeterminate" warning — and the probe tool documents that SIGKILL leaves the file mutated.
Every exit outside the documented verdict set aborts.

**The classifier's own terms are a suppression input too (added 2026-09-17, and the
rule below is all that survived of it).** A class pattern
that matches too widely removes findings from the unmatched-intake pile with no signal that
anything was dropped — `|| true` aimed at the review machinery rather than at code. So a new
class term is judged on its FALSE POSITIVES first: name the unrelated findings it would
claim, and pin them as negatives in the same commit. Under-matching leaves a finding in the
intake pile where a human sees it; over-matching hides it. Two consecutive rounds of one arc
were spent narrowing a single added term (`cleanup path`, then `caller state`), which is what
this rule exists to skip.

And when narrowing does not converge, SUBTRACT. Round after round of one arc went on terms
added to this table; the terms were removed rather than sharpened again,
because this file's own policy is to prefer to miss and its header already records that
successive regex layers trade one imprecision for another. A shape that keeps drawing
findings is telling you the vocabulary does not exist, not that you have not found it yet.

That is what happened to the term added for THIS rule: round after round, each finding
correct, each attacking the phrase the last one added, because every way of naming the
classifier's own machinery also names ordinary ingestion and queue findings. No matcher
vocabulary for it exists in the table now. Findings about the class table stay in the
unmatched pile and get an `instance-only` disposition, which is the honest record: they are
artifacts of editing the table, not a defect class in the product.

### 4. Vacuous witness (107 findings)
For every new/changed test, reason the mutation through before committing: *if the
load-bearing line were deleted or inverted, does this test actually red?* Traps seen
repeatedly: presence-check standing in for behavior (asserting a variable is set, not
that the writer honors it); a witness that dies before reaching its discriminating
assertion (KeyError before the emit); a child process that never instantiates the
thing under test; an assertion after an early return; and, in a doc or prose witness, a
needle on a list marker, heading or label (`- **K5 —`, a bare `checkpoint`) instead of the
claim text after it — invert the claim, keep the marker, and the test stays green (U-HE-39,
merge-gate witness lens r1: K5, K7 and K8 of the four K-dispositions pinned only by their bullet). For a
doc witness the mutation to reason is *negate the sentence*, not *delete the line* — and a
claim-text needle that stops mid-sentence is the same defect one clause later: pin the WHOLE
claim, matched against the file with its whitespace flattened so a wrapped sentence is one
string (U-HE-39 r2: K7's "shadow mode only" clause sat outside a first-half needle). Where
feasible, actually run the
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

**Shell half (added 2026-09-17, lane-init `_LI_SRC`).** A SOURCED file mutates its caller's
shell the way `os.environ` mutates a process — the variable outlives the call, for the life
of that interactive shell, and can clobber a caller's own name. So every variable a sourced
file introduces owes the same question as an `os.environ` write: *who unsets it, on which
paths?* The answer must be ALL of them — success and every failure arm — because the one
path that forgets is the one a lane actually takes. Read the file's existing cleanup sites
first: if it already unsets its locals at every one of its exits, a new local that appears at one
is not a smaller version of the convention, it is the exception that breaks it.

This half has NO surviving vocabulary in class 7, and that is the finding, not an
oversight. `caller's shell` was tried and WITHDRAWN: it claimed a finding this class does
not own, and under the prefer-to-miss policy a term that steals from the unmatched pile does
not earn its place. That claim is EXISTENTIAL — one such finding exists — and an existential
claim survives a growing corpus, because a later row cannot unmake an earlier one. What is NOT
restated here is any CATEGORICAL or PRECISION claim (how many it matched, what share were
wrong): the gate log only grows, including with the reviewing arc's own findings, so those are
true at one anchor and false at the next. That is the whole distinction, and it is why the
decision below rests on policy rather than on a measurement. Re-derive with
`refresh-classes.py` if you want the current numbers. And
`tools/test_refresh_classes.py::test_class_7_does_not_claim_sourced_shell_caller_state`
now pins the absence. A shell-sourcing finding therefore lands UNMATCHED, which is the
intended outcome: unmatched is where the next class comes from. The rule that removed it
still stands, and is why it went -- terms like `caller state` or `caller-scoped` read just as naturally in ownership,
aliasing and scoping findings, and stealing one of those is worse than missing it — a class
hit is what removes a finding from the unmatched new-class pile, so an over-wide term
silently switches the intake loop off for everything it claims.
Any `os.environ` write: who restores it, does the restore survive a mid-test
`monkeypatch.undo()` (use an INDEPENDENT `MonkeyPatch`), does it leak into suites that
assert the namespace empty (`HARNESS_*` must never escape tools items), and — the P1
shape — does the variable serve MORE THAN ONE consumer meaning? Enumerate every reader
of the variable before repurposing it.

### 8. Subprocess boundary (58 findings)
Monkeypatching a Python seam cannot reach a child process — only inherited env can.
Children get a COPY of env at spawn; later parent changes don't propagate. Nested
sessions of the same tool (pytest-in-pytest) re-run your own hooks against
already-modified state — first-writer-wins any value that must survive nesting. A token derived from a filename or
other authored text, interpolated into a command STRING another tool runs with `shell=True`,
is shell-live even when your own call passes an argv (u-he-40 codex r3 P1: a test file named
`tools/test_$(id).py` reached `mutation_probe.py --test`) — `shlex.quote` it at the
interpolation; the outer argv does not protect the nested shell. And `python -m <tool>` searches
the working directory first: with `cwd` set to an untrusted tree, a `<tool>.py` there runs
instead of the tool (u-he-40 codex r5 P1) — invoke the tool's absolute executable.

### 9. Path / default resolution (56 findings)
Any path computed from env-or-default: TRACE the chain to the concrete path it lands
on when NOTHING is set, and write that path into your review — "falls back to
`~/.reports/` (the operator's real store) when the env var is unset" is a *named
finding*, not an implementation default to read past. Def-time constants bake the env
at import (`QUEUE_DIR`) — a later env change does not reach them. A worktree does NOT
isolate `$HOME`-absolute paths; isolate by ENVIRONMENT. Paths read back from git are data too: without `-z`, git quotes and
escapes any name holding non-ASCII characters, tabs or quotes, so a suffix test on
`test_é.py` silently fails (u-he-40 codex r7) — request NUL-delimited output.

### 10. Fixture scope / lifecycle phase (35 findings, but two P1s)
pytest specifics that shipped defects: a per-item bracket covers setup+call+teardown
but NOT collection/import time or session-fixture teardown after a foreign final item;
higher-scope teardown runs inside the CURRENT item's teardown phase (measured);
`conftest` runtest hooks fire for items ANYWHERE in the run unless path-guarded; a
function-scoped autouse fixture covers only the test body.

### 11. New authority-bearing command surface (added U-HE-47; 5 findings in one arc)
Fires the moment a diff introduces a NEW command, verb, or recipe whose effect can
mute, dispose, suppress, or authorize anything (an adjudication, an exemption write,
a gate override). Before committing, answer ALL FOUR — every U-HE-47 review round
2–5 finding was one of these, discovered serially at a full round each:
(a) **Guard venue**: how does the permission guard see it? A generic-prefix allow
auto-approves every argument shape — an authority-bearing verb needs an exact-shape
validator (arity-bounded, enum-pinned submodes, identity-pinned actors), with the
dangerous submodes left at ask. (b) **Authority half**: the guard validates FORM
only — what binds the CLAIM to real state? Caller-supplied text (an env prefix, a
flag value) is not authority; bind to holder/reservation/store state the caller
cannot choose (the record_phase pattern). (c) **Carrier parity**: every runner's
carrier (.claude skill, .agents bridge/projection) must document the SAME invocation
the guard actually allows — a bare documented form against a prefix-requiring guard
strands headless at ask; identities parameterize per runner. (d) **Production-call
witness**: a static test must pin the documented command shape in each carrier —
helper-level tests stay green when the production instruction is reverted.
**Sweep-altitude rule (U-HE-47 r2→r5, four rounds on one verb):** at the FIRST
reviewer finding on such a surface, do not fix only the named token — enumerate
EVERY degree of freedom of the command (each argument, each identity, each env
input) in a table with its pinning authority (enum, identity set, holder state,
ask-gate), and close them ALL in that absorption. The sibling sweep's unit is the
mechanism's whole authority surface, never the literal flagged shape — otherwise
the reviewer walks the remaining dimensions one full round each.
**Executor surfaces fire this class too (u-he-40 codex r2: two findings on one grammar).**
A diff that adds a check or tool which EXECUTES command text taken from authored input — a
commit message, a PR body, a claim line — has built an authority-bearing surface: the text
is caller-supplied and the executor is its authority. Enumerate the accepted grammar's
degrees of freedom before committing: extra positional tokens (`just a b` also runs recipe
`b`), option tokens with side effects (`pytest --basetemp=<dir>` deletes that directory),
path segments (`tools/../x.py`), and recursion (a recipe or script that runs the executor
itself). Parse each claim into a pinned argv — exact arity, enumerated verbs and flags, a
denylist derived from the file that defines it and pinned by a test — never a token
character class followed by `*`. A test-running shape is never read-only here: a named test
can be a billed live e2e run with inherited credentials (u-he-40 codex r3 P1) — allowlist
exact provider-free commands instead of admitting a grammar. And pinning a command NAME is not
pinning what runs: a recipe, script, alias or config file the subject tree defines is
subject-controlled (u-he-40 codex r4 P1: an allowlisted `just lint` ran whatever the subject's
justfile said), so an executor runs trusted tooling from its own environment against the
subject — never the subject's recipe bodies. The same holds for a trusted SCRIPT named by a
relative path: inside a replayed or checked-out tree, `tools/x.py` is that tree's copy (u-he-40
codex r5 P1). A check that must execute subject code (tests) cannot be replayed against
historical trees in the reviewer's environment at all — refuse it rather than sandbox by hope.

### 12. A quoted contract phrase with no line behind it (added U-SR-01; both of the u-he-35 arc's P1s)
*(u-he-40 codex r4: a docstring quoted C-HE-31 §4(b)'s "rolling" windows over code that cut
fixed partitions counted from promotion — the adjective was the undischarged phrase.)*
Fires whenever the diff QUOTES a contract — a spec phrase in a docstring, a
requirement copied into a verification-manifest row, a comment restating what the
code guarantees. Ask it per phrase: *which line discharges this?* Name that line. An
answer of "the mechanism generally does that" means the phrase is undischarged, and
an undischarged phrase is another finding on layaway — the wording of a guarantee
sitting in the place the guarantee was supposed to go, and reading, to every later
reviewer, exactly like the real thing.

Both P1s of the u-he-35 arc were this shape, and both were spec-verbatim misses at
turn 0 — the deciding text was in the session's own context before the first line
was written:
- `codex_review.py`'s own docstring said "the exit code is a convenience, never a
  verdict," and the loop skill body said a verdict counts only on its schema parse
  (C-HE-15), never on exit code or silence. `returncode in (0, 1)` shipped as the
  verdict anyway.
- The spec's "result row required before pilots" was read at grounding and copied
  verbatim into the arc's own manifest row. Nothing enforced it. Four rounds
  (r1, r5, r9, r10) went to re-litigating a gate the row already claimed.

The rationalization arrives in the voice of diligence: *"the plan skeleton already
shows `returncode in (0, 1)` — I'll follow the plan."* That is plan-over-spec
deference. A plan skeleton sketches SHAPE; it never grants CONTRACT, and where the
skeleton and the quoted phrase disagree the phrase wins and the skeleton is the
finding.

Two exits, and only two. **Discharge it** — write the line number beside the phrase.
Or, if you believe the phrase is wrong, **route it**: a quoted spec requirement is
BINDING, so disagreeing with it is a Class 1 fork to design-phase back-flow, not an
edit you make on your own authority. What is never an exit is deleting the quote and
describing what you built instead: the requirement outlives the sentence, so that
move leaves the violation in place and removes the only evidence of it. Both P1s
above stay defective under it — exit-code-as-verdict is still wrong once the C-HE-15
quote is gone, and the pilot gate is still unenforced once the row stops claiming it.
Silent absorption is the worst failure mode this workspace has; a docstring is a
cheap place to commit it.

### 13. A new command the loop must reach (added U-SR-01; u-he-35 r2, one round)
Class 11 asks what a new verb can AUTHORIZE. This asks the other half: can the loop
INVOKE it at all? The trigger is mechanical — the diff adds a justfile recipe (or any
new command shape) whose verification-manifest `runs_in` includes "loop" — and equally a
diff that CHANGES a documented command shape in a carrier to fix what the command records
(an added env prefix, flag or argument): that fix is only as durable as the pin on it
(U-HE-39 witness lens r3: a `HARNESS_LANE_ID=` prefix added to six carrier lines shipped
unpinned, and the one existing assert matched the command with or without it). Answer
both halves: is the permission guard wired to auto-allow the EXACT shape the loop
will type, and does a witness pin that shape so reverting the wiring goes red? The
precedent commits already model the whole chain — recipe ⇒ guard allow ⇒ witness
(U-HE-25, U-HE-34); match one of them instead of inventing a fourth arrangement.

The temptation is the harmless recipe: *"it only publishes a log — there's nothing
dangerous here for the guard to gate."* Danger was class 11's question, and the two
questions come apart precisely here. The guard's silence on a harmless verb is not
permission; it is an ask prompt — and an ask prompt inside a headless lane is a
stall with nobody awake to clear it.

### 14. Signal handler meets lock (added U-SR-01; u-he-35 r10)
Any signal handler in a process that also takes locks, or any handler touching state
a lock guards. The fact that decides the answer: in CPython a Python-level handler
always runs on the MAIN thread, whichever thread the signal was delivered to. So ask
*which* thread holds the lock when the signal lands, because the two arms fail
differently:
- **Main thread holds it** — the handler is the lock's own owner. An `RLock` lets it
  straight back in and the handler walks into the middle of a half-finished update
  the lock existed to hide; a plain `Lock` deadlocks against itself instead.
- **A worker holds it** — the handler is not the owner, so it BLOCKS, waiting inside
  a signal handler for a lock it cannot hurry. If that worker needs anything the main
  thread was going to do, the wait never ends.

The trap is assuming one arm is the whole story: an `RLock` looks like protection
against the first and buys nothing against the second. Same family as the recorded
fork-while-holding-a-lock deadlock — the hazard is asynchronous control transfer
while a lock is held, whichever way control goes.

*"The handler only sets a flag"* is the sentence to distrust — first because the
flag's readers may assume it changes only between guarded sections, and second
because the handler that only sets a flag this round grows a cleanup call the next.
Keep handlers to what is async-signal-safe (set a flag, write one byte to a
self-pipe) and let an ordinary thread do the work under the lock.

### 15. Bound bytes are not the executed bytes (added preflight-finding-intake; 10 rows at the 2026-09-16 corpus, 2 of them this exact shape)

A check, reviewer, or classifier runs against the **working tree** while the record it
produces binds the **committed** `base..HEAD` range — so an uncommitted edit can make
the check pass, the attestation records HEAD, and the edit is then reverted or never
lands. The 2026-08-19 wrapper finding ("the reviewer runs against the live worktree
while the binding covers only the committed diff") and this arc's own codex r1 P2
(the class table read from the tree while the sweep attestation bound HEAD) are the
same defect. **Question:** *for every artifact whose record names a binding, do the
bytes it actually read come from that binding (`git show HEAD:<path>`, `base..head`
diff), never from the tree?* If a test can make the check pass by writing a file
without committing it, this is the class.

### 16. The witness codifies the divergence (added class-16-codifying-witness; 14 rows at base `63e19e3ee`'s 2,162-finding log, every one of them unmatched until this class)

The diff departs from a cleared contract, and the test that ships with it asserts the
**new** behavior. The witness is green, non-vacuous, and fires — and what it now protects
is the departure. Review reads a covered change; the breach arrives with regression
armour. Class 4 is its sibling and not its twin: a vacuous witness proves nothing, this
one proves the wrong thing — and the corpus agrees rather than the reasoning alone, since
all 14 rows matched no class at all at that anchor, class 4 included.

Recorded shapes, all the same move: *"the new merged-holder test codifies this contract
drift while the clearance claims no spec contract changed"* (`arc_metrics.py:564`); *"the
rewritten test now expects the sibling R-999 row, so it blesses rather than detects this
regression"* (`arc_exit_report.py:600`); *"the new row-order test enshrines the opposite
contract"* (`loop_cost_baseline.py:47`); *"the added failure test asserts the warning
rather than failure, so it codifies the contract drift"* (`lane-init.sh:479`); and CI
itself doing it — *"test_codex_workflow_parity.py even requires the omission, so CI
codifies the admitted cohort gap instead of detecting it"* (`ship-pr/SKILL.md:208`).

**Question:** *for every assertion I added or changed, would the cleared contract's own
text predict this expected value?* When the expected value is what the code now does
rather than what the contract says, this is the class.

*"I updated the test to match the new behavior"* is the sentence to distrust — it is
this defect and a legitimate contract amendment, worded identically. The discriminator is
what else is in the diff: a real amendment carries the spec/plan change (or a filed fork)
beside the test; this one carries only the test edit. If the contract is genuinely wrong,
route it — do not let the witness ratify the change on the contract's behalf.

### Vocabulary evaluated and LEFT OUT — "a record's field contradicts its own body" (2026-09-18)

The shape is real and has **two measured instances one arc apart**. `B-282` shipped
`status: open` while its own summary said U-HE-40 is HELD — and `OPEN_STATUSES` includes `open`
and excludes `held`, so `--open` counted a row its author had described as blocked. One arc later
a U-HE-45 plan tick marked a **combined** step `[x]` while the paragraph beneath it said half that
step was never performed, against a convention defining a checked box as "carried out". Four
corpus rows carry it. Re-reading the prose catches neither: both are visible only by asking *what
does the consumer do with this field?*

**It is not a class, because the vocabulary cannot tell prose that DESCRIBES a field from prose
that SETS one.** Three review rounds, each trading one imprecision for another: two independent
tuple patterns matched across *sentences*, fixed with class 16's window; the same terms then
matched unrelated text *within* one sentence ("The status field is parsed correctly even though a
missing verdict file makes the unrelated hook fail"), which no window can separate; and `mark`
without a word boundary matched inside `benchmarks`. The middle one is terminal — the same wall
the owed-pointer vocabulary hit, one floor down: the distinction is **semantic**, not lexical.

The asymmetry that decides it, as ever: a false match is worse than `unmatched`, because
unmatched OWES an intake line while a match silences it. An arm that cannot separate those two
readings actively hides the new classes this table exists to surface.

**Sweep it by hand, because the question is still worth asking:** *for every status, disposition
or checkbox this diff SETS — does the body of that same record agree with it, and which consumer
reads the field rather than the body?* Name the consumer. `--open`, a tick-count derivation and a
reducer all read fields; none read paragraphs. *"The prose explains the nuance"* is the sentence
to distrust: it may explain it to a human, but the field is what the tooling acts on.

### Vocabulary evaluated and LEFT OUT — "the owed pointer refresh" (2026-09-18)

The shape is real and recurs: a diff finishes the work and leaves a surface *consumers read
to decide what to do next* still naming what was just finished. Nothing is wrong in the code;
the ROUTING is wrong, so the next reader — or the next `/roadmap-continue` — is sent back into
completed work. Recorded instances: *"declares Step 5 executed and the fence live, but HEAD's
`.harness/roadmap_status.md:25` still says the frontier is …"*; *"declares the operator gate
complete … but the canonical implementation plan still leaves Step 5 unticked"*; *"marks both
operator decisions ratified, but the same plan's current version summary at line 38 still says
they are open"*.

**It is not a class, because the vocabulary cannot carry it.** It shipped as class 17 on the
U-HE-45 arc and was subtracted at that arc's round 5. Its findings fell in rounds 2, 3 and 5 —
three rounds, not three consecutive ones — so the two-consecutive trigger fired at r3, where it
was fixed rather than withdrawn; each round traded one imprecision for another: `(?:never|not |un)refreshe?` gave the `never` arm no separator and so
missed the plainest wording, hiding behind a different arm the arc's own finding happened to
match; `just completed` / `already landed` need not describe the pointer, so *"The live pointer
just completed validation successfully"* matched while reporting no staleness; and
`still (?:says|names|points)` has **no polarity**, so *"The live pointer is fresh and still
points to the intended next unit"* matched — a CORRECT pointer read as a stale one. Polarity is
the part a regex cannot express, and each fix bought exactly one more round in which to find
the next false surface.

The asymmetry that decides it: a false match is worse than `unmatched`, because unmatched OWES
an intake line while a false match silences it — so an over-broad row actively hides the new
classes this table exists to surface. Subtracted per the rule that an adversarial-hardening
loop does not converge by adding layers.

**Still sweep for the shape by hand.** The question is worth asking even with no row to fire
it: *does this diff complete something a live pointer names — and does the diff move that
pointer?* If the unit's own scope lists a pointer refresh among its deliverables, the diff is
not complete without it. The temptation sounds like protocol — *"the refresh is its own PR by
§12.2.1"* — and §12.2.1 forbids only the reserved TITLE PREFIX on a bundled PR, not the
bundling. On the arc that surfaced this, the substantive defect is registered as `B-288`, where
prose carries the polarity a pattern could not.

### 18. The code departs from a cleared contract (added merge-door-release-verb; at the
2,247-finding corpus the pattern matched 26 rows and the class CLAIMED 23 of them —
earlier classes take the other 3 — and 14 had matched no class at all)

The implementation states something a cleared `C-HE-*` contract explicitly denies. Not a
stale count, not an undischarged quote, not a test blessing the change — the code itself
asserts the opposite of the contract, and usually because the contract was never re-read
while the code was being narrowed.

Recorded shapes: a holder gate admitting a terminal `merged` reservation against C-HE-03
§6's explicit prohibition (the SAME defect across six rounds, which is what makes this a
class rather than an incident); an audit declaring a canonical C-HE-30 statement false
while saying no spec edit is owed; a conflict rate reported as an interval where canonical
C-HE-13 §4 still requires the real rate; and this arc's own `TERMINAL_NOT_GREEN`, which
honoured `TIMED_OUT`/`STARTUP_FAILURE`/`ACTION_REQUIRED` although C-HE-19 §1 declares the
CI outcome domain to be exactly `{SUCCESS, FAILURE, CANCELLED}` — widening a
terminal-state contract on a lane's own authority while that lane's spec amendment
explicitly promised not to.

**Question:** *for every constant, enum, allowlist or predicate this diff adds, does a
cleared contract already declare that domain — and did I re-read it, or infer it from
what the code around me happened to accept?* An enumerated set is the high-risk shape:
it looks like a local implementation detail and is frequently a contract's domain
restated from memory.

Two exits, as class 12: discharge it (cite the contract text that admits your value) or
route it (a domain change is the contract owner's call). What is never an exit is
widening quietly because the wider set "seems safer" — a larger admissible set on a gate
is strictly less safe, and it is the contract's job to say how much less.

*Distinct from its neighbours, which is why it is its own class.* Class 12 is a contract
phrase QUOTED into the diff with nothing discharging it — the words present, the line
missing. Class 16 is the WITNESS asserting the departed behaviour, so review reads a
covered change. This is the CODE half, whether or not any prose quotes it and whether or
not a test blesses it. The cluster was already visible to class 2's note, which refused a
bare `contradict` because it "sweeps that whole cluster in, the same wrong direction as
`drift`" — correct for class 2, and the reason these rows sat unmatched: they needed
their own home. The pattern binds `contradict` to `C-HE` for exactly that reason.

*(Class 1 also gained `symlink` in the same pass: its containment rider already described
the O_NOFOLLOW idiom, but the vocabulary did not carry the word, leaving 10 containment
findings — a dangling link read as absent, a link followed without containment —
unmatched at the same corpus.)*

### Vocabulary evaluated and LEFT OUT — "the guidance prescribes what the contract forbids" (2026-09-18)

Class 12 catches prose that QUOTES a contract and discharges nothing. This is its inverse:
prose that PRESCRIBES an action a cleared contract forbids. Recorded instance — a ship-pr
recovery section told operators to unblock, release the merge-door lease, and land a repair
when post-merge CI reds on the landed commit's own bytes, while C-HE-06 states the lease is
never released until that run is confirmed and defines no repair-PR exception. It is the
more dangerous direction: an undischarged quote is inert, whereas a prescription is executed,
and in this workspace guidance prose is read by agents that do what it says — so the defect
launders a contract breach into documented practice.

**Not a class, on measurement.** Against the live 3,288-row corpus, `instructed to violate`,
`without amending`, and `violate[s] the committed` each matched exactly ONE row — this
finding's own. The nearest neighbour (`the committed plan instructs operators to run
merge-door-unblock with that refresh PR, so the documented recovery command always fails`)
is a DIFFERENT failure: documented guidance that fails loudly, not guidance that succeeds
and breaks an invariant. Cardinality 1 with no discriminating vocabulary is precisely the
shape the two subtractions above were subtracted for, and a false match costs more than an
unmatched row because it silences the intake line.

**Sweep it by hand. Question:** *does any prose in this diff tell a reader to DO something
— a command, a recovery, an order of operations — that a cleared contract forbids?* The
exits are class 12's: discharge it (cite the contract text that permits it) or route it (a
spec amendment or carve-out is the contract owner's call). Deleting the contract's name
while keeping the instruction is the worst of the three, and the most tempting, because the
prose then reads clean. Promote this to a real class at a second instance.

### Vocabulary evaluated and LEFT OUT — "the validator reads a sub-span" (2026-09-17)

The shape is real and recurs across arcs: a guard, parser or check examines PART of its
input — one element, one cell, one field, a prefix — and treats the remainder as if it had
been inspected. Not an error swallowed (class 3's shape) but an input never looked at.
Recorded instances: *"Only the first `-e/--regexp` value is examined"*; *"Self-resume
validates only lane_id and PR"*; *"`_valid_head` validates only that arc_id and state are
strings — a head with state `opne` is accepted"*; *"`read_pairs` validates only that one
denominator header exists"*.

**It is not a class, because the vocabulary cannot carry it.** Three attempts were measured
against the live corpus and all three failed the precision bar: `only the first|unanchored`
took 10 rows across 9 arcs but two were different defects, one of them reading too MUCH;
`validates only|never validates|does not validate` took 7 across 7, but the last two
alternatives match TOTAL absence of validation, which is a different defect — the class's
own witness row inspected no part of its input; `checks only|requires only|examines only`
reached 21 rows at about 71% precision. The discriminator needed is a conjunction — an
inspected portion AND an uninspected remainder — and a finding's free text does not reliably
carry both halves. Since a false positive REMOVES a row from the unmatched pile where new
classes are found, precision-first governs, and nothing met it.

**Catch it by hand instead. Question:** *does this check consume its WHOLE input, or does it
match a span and let the rest through?* An anchored `fullmatch`, an all-elements loop, or a
parse into a typed model consumes everything; a `search`, a `[0]`, a "contains" test, or a
regex without `^…$` does not — and what it does not read, it silently accepts.

**The highest-risk site is a read you introduced THIS round to satisfy a different
finding.** When an absorption replaces an inference with an authoritative read — a ledger
query, an API call, a ground-truth lookup — the sweep's attention is on whether the new
source is the right one, and nobody re-asks the sub-span question of the brand-new parsing
code. That is where it lands: a 2026-09-18 arc swapped a proxy for a real CI query and, in
the same commit, took `done[0]` from the run list (ignoring a second run still pending) and
filtered it on `event` alone (ignoring which branch the run belonged to) — two instances of
this exact shape, both in three lines written to close a different defect, both found by the
next reviewer round. A new read is new input; parse all of it.

The trap is that each part-check looks complete while you are writing it, and the gap names
itself one reviewer round at a time. The arc that recorded this watched one validator take
four rounds that way — a suffix inside a token, a duplicate entry, the text between tokens,
a range after the final token — each fix guarding the span the last one had just made safe.
Then the *fix* for that repeated the shape twice more: a tightened boundary that made a
malformed pointer stop matching, and so dropped it from the checked set instead of failing
on it. The sentence to distrust is *"that case can't appear here"*: it is a claim about
input you have chosen not to inspect. When a fourth guard is going onto one validator, the
answer is almost never a fifth — it is one anchored, total check.


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
   grounds, or it is held per step 4), append the disposition —
   `HARNESS_ARC_ID=<arc-id> just merge-gate-adjudicate --finding-id <id>
   --disposition accepted|rejected --actor <runner>_absorber` (`accepted` = the fix
   was applied; `rejected` = refuted; the finding_id is on the round's emitted JSONL
   rows). EVERY finding gets one of these two, always: an absorber writes no third
   state, and no finding may be attested past with `disposition=null` — see step 4
   for why holding is not the exception it looks like. The
   `HARNESS_ARC_ID=` prefix is
   REQUIRED — the guard auto-allows only the prefixed form, and the CLI holder-binds
   it to this lane's live reservation. The actor is the RUNNER's own absorber
   identity — `claude_absorber` on the Claude runner, `codex_absorber` on the Codex
   bridge — never the producer, never `operator`. Without this row the finding stays disposition=null forever and N6 counts
   nothing — the attest below records that you ANSWERED the finding, never that it
   was DISPOSED.
4. **A finding you HOLD owes a fail-closed probe in the same round.** Holding is the
   cheapest-feeling disposition in the loop, and it arrives sounding like good scope
   discipline: *"that's a later unit's job — the plan already schedules it."* The
   scope call is often right. What is never right is holding it BARE. In the same
   round, land the minimal thing that fails loud when the held condition is violated —
   one assertion, one refusing row, one guard — and the hold becomes a scope decision
   with a floor under it. Held bare it is a promise, and the reviewer does not take
   promises: the u-he-35 pilot gate was held at r1 and then re-litigated at r5, r9,
   and r10 — four paid rounds on one unpromoted hold, the costliest policy miss of
   that arc (charter WR-06, [A] §1).

   **"Held" is not a ledger state, and reaching for one is the error.** Both obvious
   moves are wrong, and they are wrong in opposite directions. Writing `suppressed`
   names its actor as the *adjudicating authority*, which C-HE-24 §5 restricts to a
   decorrelated lens, a deterministic rule, or a logged operator override — an
   absorber is none of the three, so the row asserts an authority that never existed.
   Leaving the row null and naming the finding in the sweep is worse in a quieter
   way: `unanswered_findings` subtracts every id an attestation names, and it never
   reads disposition, so the obligation disappears permanently while the ledger still
   says nothing was decided. One move fakes a verdict; the other loses the finding.

   The way out is to notice that the probe already IS the disposition. If you landed
   the fail-closed floor, you FIXED this finding — the risk it named is now caught —
   so it is `accepted`, and what remains is not this finding at all but a separate
   scope item: the policy, the real ceiling, the proper owner. Register that as its
   own forward row where forward work lives. A reviewer's finding and the scope it
   brushes against are two objects, and collapsing them is what made "held" feel
   necessary.

   And if you cannot land even the minimal probe, you have no disposition to write —
   so do not attest past it. That is the genuine operator gate: halt, surface the
   finding, and let the operator direct the fix or write the `suppressed` row on
   their own authority, which is the logged override the contract names. The
   permission guard's `accepted|rejected` allowlist (`_adjudicate_exact_shape`,
   U-HE-47) is that boundary made mechanical; never widen it to get past this moment.

5. If the class was absent/unfired in this file, repair the skill in that commit too
   (the loop below).
6. When two consecutive rounds' findings target mechanisms YOUR absorption invented
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

**The loop is enforced at the sweep attestation, not remembered.** This obligation
executed zero times across the ten absorption commits of U-HE-35 while it lived only
in this prose (charter §1, "nothing flows in"). So `just review-template-sweep`
classifies every outstanding reviewer finding against `scripts/refresh-classes.py`'s
table (its `classify` verb) and stamps the result above each finding; a finding that
matches NO class is marked `UNMATCHED` and pre-filled with an `intake:` slot that
`just review-attest-sweep` refuses to leave empty. Exactly one of:

- `intake: class-extended <class-number> <what changed>` — you extended a row in
  `refresh-classes.py` (and this file) so the finding now matches;
- `intake: new-class <name> <what changed>` — you added a class in both places;
- `intake: instance-only <why no class should carry it>` — a genuine one-off.

A repair claim is **verified, never trusted**: attest re-classifies with the live
table, and a finding still unmatched under `class-extended` / `new-class` refuses the
attestation until the row lands (or the disposition becomes `instance-only`). A
finding whose repair landed simply matches and owes no intake line. `instance-only`
dispositions are recorded on the sweep attestation (`intake_instance_only`), so the
escape hatch's rate is measurable — an arc that dispositions every unmatched finding
as a one-off has answered the letter of the loop and none of its intent.

**Staleness check:** `scripts/refresh-classes.py` (no verb) re-clusters the live gate
log and prints per-class counts plus recent findings matching NO known class — those
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
fix now must be named in the commit message or register, never silently carried — and
naming is what stops a hold being *silent*, never what makes it *safe*: a held finding
still owes the same-round fail-closed probe (step 4 of the sweep above). Then
commit and invoke the reviewers — they should be confirming, not discovering.

Since B-215, the named-answer set is ATTESTED, not merely written — and since
U-SR-04 (charter WR-10) the labels come BEFORE the answers: after the final
commit, generate the answers file with `HARNESS_ARC_ID=<arc-id>
HARNESS_LANE_ID=<lane-id> just review-template-preflight <answers-file> origin/main` — the
destination must live under `.harness/tmp/` (the gitignored scratch namespace; the
verb refuses anywhere else, keeping attestation artifacts out of the stop-gate's
tree-dirty view). It runs
`preflight-grep.sh` over the attested range and writes every hit label into a
fresh template ([B] F14: three attest calls failed by trial only because answers
were authored before the labels existed). Fill every placeholder with the named
answer — attestation refuses a file still carrying one, and a deleted placeholder
is not an answer either: every label section and finding line must carry content
beyond what the template wrote — then attest with the
same-prefixed `just review-attest-preflight <answers-file> origin/main`. The inline prefix is
REQUIRED on both verbs exactly as for the review itself (they resolve the arc via
env_arc_and_lane(); a bare invocation binds the branch-* fallback arc, not the
reserved one). The review wrapper refuses round 1 of a reserved arc without a
live attestation (`tools/review_loop_gate.py`; the attestation binds head+diff,
so template + attest after the last commit — the template never overwrites, so
each round's answers file gets a fresh path). The "after every review round"
sweep ends the same way: absorb, commit, `HARNESS_ARC_ID=<arc-id>
HARNESS_LANE_ID=<lane-id> just review-template-sweep <answers-file>` (the prefix
matters here too — a bare invocation queries the branch-* fallback arc's
obligations, finds none, and declines; prefixed, it pre-fills every outstanding
finding_id token-exactly plus the range's hit labels, obligations spanning both
loop channels and all rounds), fill, then the same-prefixed
`just review-attest-sweep <answers-file>`.
