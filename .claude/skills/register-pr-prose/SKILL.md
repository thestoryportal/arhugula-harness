---
name: register-pr-prose
description: Authoring discipline for every piece of durable prose in this workspace — PR bodies, register close_outs (.harness/forward-register.yaml, post-phase-8-forward-register.md), arc-ledger entries, checkpoint files, and any docstring or comment that states a checkable fact. Use WHENEVER writing or updating a PR body, a register row, a close_out narrative, a grounding-pass section, or prose containing counts, §-cites, line numbers, or claims about what a mechanism does. Prose findings are the second-largest defect class in this workspace (145 of 1,084 findings at first distillation, 2026-08-24) and cost full gate rounds; this skill is how the prose passes the spec-conformance lens on the first read.
---

# register-pr-prose — durable prose that stays true

## Why this exists

145 of the 1,084 findings at first distillation (2026-08-24) in this workspace's gate log are prose defects: stale
close_outs, drifted counts, wrong §-cites, absolutes falsified by a later commit.
Each one costs a gate round. The root cause is always the same: **prose states a
checkable fact without binding it to what makes it true**, and then the tree moves.
Every rule below is a binding discipline, and each earned its place by a real BLOCK.

## The six rules

### 1. No bare counts — bind or delete
"Six witnesses now" was checkably wrong twice in one arc; a call-site count was wrong
on arrival. A number in prose is a copy of the tree that nothing redraws. Either bind
it ("six, at `d68d15e72`", "at the round-8 head") or replace it with the pointer that
always resolves ("the witness module is the source of truth", a bare `rg` invocation).
Same for line numbers: prefer a grep anchor or symbol name over `file.py:123` — your
own next edit shifts it.

### 2. State mechanisms round-bound, never as current-state
A close_out written mid-arc describes the mechanism *as of that round*; later
absorption rounds falsify present-tense sentences ("un-isolated child processes ALL
resolve the belt" became false when round 13 carved an exception). Write "round 12's
mechanism: …" not "the mechanism is …", or write the close_out ONCE, after reviewer
convergence — see rule 6.

### 3. Verify every cite by reading it now
Before writing `C-XX-NN §M` or any spec/plan cite, open the cited section at HEAD and
confirm it says what you claim — never cite from recall (an append-only claim cited §2
when the guarantee lived at §1; three carriers shipped the error). For contract/unit
cites, `just overlay-query` resolves them deterministically. A cite you didn't just
read is a cite the spec lens will read for you, in a BLOCK.

### 4. No implied partitions or absolutes
Numbers presented together read as arithmetic ("6288 synthetic + 82 real of 6589"
implied a partition; the balance was a third category and the sentence didn't
reconcile). If categories don't sum to the total, say so explicitly. Sweep "all",
"every", "only", "never" — each is falsified by a single future exception; either
scope it ("every consumer but one, below") or drop it. When you legitimately add an
exception to an absolute elsewhere, grep the sibling carriers and qualify them in the
same commit.

### 5. Name residuals; supersede in place
A known-but-unfixed issue is written into the record with its bound ("the 7c driver
leaks its mkdtemp root on already-failing arms — judged non-blocking"), never omitted.
When amending a long-lived record, stamp the correction in place and sweep every
carrier of the old claim in the same round — an appended correction leaves the stale
text standing as a second authority.

### 6. Sequencing: durable prose is written once, at the end
Update register close_outs and PR-body mechanism sections AFTER reviewer convergence,
not incrementally — a mid-arc close_out cost two gate rounds in one arc because each
later absorption made it stale again. During the arc, keep facts in the commit
messages (which are inherently head-bound); assemble the durable narrative once the
tree stops moving.

## PR body structure

Assemble in this order (sections may merge for small arcs, but each concern appears):

1. **What** — one paragraph, plain language, what changed and why.
2. **The defect / the ask** — grounded: measured numbers WITH their measurement head.
3. **The mechanism as landed** — written post-convergence, exceptions named inline.
4. **Witnesses & probes** — what pins each property; state probe results as measured
   facts ("deleting X reds Y"), and say which claims were probed vs reasoned.
5. **Verification at head `<sha>`** — suite results, lint/type gates, each bound to
   the sha it ran at. A result from an older head is labeled with that head.
6. **Deliberately not done / residuals** — named, bounded, with whose call it is.
7. **Grounding pass (at head `<sha>`)** — the final section, written last: re-read
   cites at this head, recomputed counts, reviewer/CI status as it actually stands
   at publication time. Never write a grounding pass that asserts a future state
   ("both reviewers re-ran") before it has happened — publish claims only after
   their territory exists.

## When a prose finding still occurs — the skill's own repair loop

A reviewer BLOCK on prose this skill governs is a miss to classify and repair **in
the same absorption commit** (passive knowledge decays; in-commit obligations do
not): **absent** — no rule covers the shape → add or extend a rule with the real
example; **unfired** — the rule exists but didn't trigger on this phrasing → rewrite
it so the shape is unmistakable; **overridden** — it was applied and argued past →
record the override in the register and consider a mechanical check instead (a lint
for bare counts/absolutes in `.harness` prose is grep-shaped). Then add the miss as
a case in the skill's eval set (`../defect-class-preflight/evals/evals.json`, the shared suite)
so the repair is regression-tested. The skill file is tracked; git history is its
audit trail.

## Register close_out structure

- Lead with what the item WAS (the defect/gap), measured and head-bound.
- Narrate the review trail by round, each finding one sentence: what was claimed,
  what was measured, what changed. Rounds that reversed an earlier round are stated
  as such — the trail is the audit value.
- Close with the final mechanism (post-convergence), residuals, and pointers
  (PR #, merge sha, witness module) rather than restated detail.
- Before committing: parse-check YAML (`uv run --with pyyaml python -c "import yaml,sys;
  list(yaml.safe_load_all(open('<file>')))"`), run the register checker
  (`uv run python tools/forward_register.py --check`), and grep the committed file for
  your new text — never trust the editing script's own print.
