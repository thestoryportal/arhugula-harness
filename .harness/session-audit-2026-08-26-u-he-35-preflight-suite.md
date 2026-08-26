# Session audit — U-HE-35: did the self-improving skill suite fail to prevent review rounds?

**Question audited (operator, 2026-08-26).** Were there failures to proactively implement
code — at the initial implementation and at each absorption turn — that would have
satisfied the reviewers and prevented finding→absorb→re-review rounds?

**Corpus.** 29 recorded findings (2 P1 / 23 P2 / 4 P3) across 10 codex rounds on arc
`u-he-35` (gate-log rows, `producer=codex_review_wrapper`); per-round counts
{r1:4, r2:2, r3:4, r4:4, r5:4, r6:1, r7:4, r8:1, r9:3, r10:2}. The suite under audit is
`defect-class-preflight` (ten classes + `preflight-grep.sh` + new-consumer inventory +
fix-sweep meta-rules + the in-commit repair loop), plus the standing memory index the
session loaded at start.

**Headline verdict: YES — a majority of the rounds were preventable with knowledge the
suite or the session context already held.** Classification of all 29:

| Class of miss | Count | Findings |
|---|---|---|
| **A. Preventable at turn 0 — the rule was literally in context** | 7 | r1 exit-code-as-verdict (P1); r1 reps≤0; r2 guard-allow gap; r4 terminal result row; r4 decide required-series; r4+r7 reps bound (contract-derivable); r10 pilot-gate P1 (hold-policy) |
| **B. Preventable at the absorbing turn — the fix-sweep meta-rule existed but was applied shallowly to my own fixes** | 8 | r2 whole-binding; r3 regex-admits; r3 OSError escape; r5 run-level cleanup; r6 registry race; r7 escape-path unification; r9 SIGTERM-witness gap; r9 as_completed |
| **C. Arms-race latency — the stop-hardening rule existed, fired 2 rounds late** | 4 | r3 per-batch gate, r5 window wording, r7 ABA (drift family: subtraction at r7 was derivable at r3); r7 TypeError (envelope shape, inventory depth) |
| **D. Genuinely deep / weakly foreseeable** | 5 | r3 overlap witness; r4 group kill; r8 nested vendor group; r10 RLock signal-safety; r5 witness-independence P3 |
| **E. Reviewer misread, successfully rebutted (no miss)** | 1 | r5 append-window |
| **F. Re-pressed duplicates of the held pilot-gate finding** | 4 | r5, r9, r10 re-presses of the r1 live-row finding (same `finding_id` lineage twice) |

## The five load-bearing failures

**1. The two P1s were both spec-verbatim misses at turn 0.**
- r1 exit-code-as-verdict: the rule "a verdict counts only on its schema parse (C-HE-15),
  never on exit code or silence" was in the session's own operating instructions
  (roadmap-continue SKILL body) before the first line was written, and
  `codex_review.py`'s docstring says "the exit code is a convenience, never a verdict."
  I implemented the plan skeleton's `returncode in (0, 1)` anyway — plan-over-spec
  deference. The new-consumer inventory ran but answered the *happy* semantics of the
  exit codes, not the crash-aliasing case the inventory's own "half-written-at-crash"
  question mandates.
- r10 pilot-gate (escalated from r1): the spec §8.1 note "result row required before
  pilots" was read at grounding and even copied into my own manifest row at turn 0.
  The standing memory `[[merge-gate-overturns-register-and-hold-fail-closed-guard]]`
  ("hold only what fails loud + pre-action; fail-closed probe, not prose") was in the
  loaded index from session start. Applied at r1, it produces `pilot-gate-check` on day
  one and deletes four rounds of re-litigation (r1, r5, r9, r10). This is the single
  costliest policy miss of the arc.

**2. The fix-sweep meta-rule was systematically under-applied to my own fixes.**
The skill says a fix is the least-reviewed code in the arc; measured here, 8 of 29
findings (28%) targeted code my own absorptions introduced. The sharpest instance: the
r5 sweep answered class 1 with "no new coordination mechanism" while that very commit
introduced `_LiveGroups` — a new lock-guarded shared registry — whose add-vs-terminate
race was r6's finding. A factually wrong named answer passed the attestation gate
because the gate checks that labels/ids are answered, not that answers are true.

**3. The arms-race rule fired two rounds late.**
The drift family consumed four rounds (r2 head-only → r3 per-batch → r5 wording →
r7 ABA). The rule ("two consecutive rounds targeting mechanisms YOUR absorption
invented → re-scope by subtraction") permitted stopping at r5; the structural fix
(pinned worktree + frozen base sha) used only information available at r2. Two rounds
of paid review were spent hardening a mechanism whose correct form was its deletion.
Same shape in miniature: the guard reps token took four touches (any→1–99→1–9→5–9)
because each bound was invented syntactically instead of derived once from the
contract's ≥5 bar.

**4. The repair loop never ran — the suite did not self-improve during the arc.**
The skill's own obligation is explicit: classify every reviewer-caught miss
(Absent/Unfired/Overridden) and repair the skill **in the same absorption commit**,
plus add a planted-defect eval case. Ten absorption commits were made; zero contained
a skill repair. Every class this arc surfaced (guard wiring for new recipes,
signal-safety, contract-derived bounds, spec-phrase-to-code completeness) is still
absent from the skill file, and none of the greppable shapes
(`returncode in (`, `except subprocess.TimeoutExpired` without `OSError`,
`type=int` on argparse counts, a new guard `elif` without a paired witness) was added
to `preflight-grep.sh`. The suite is self-improving in name only for this arc.

**5. Attested sweeps are presence-checked, not truth-checked.**
Related to (2): the B-215 gate verifies each finding_id and grep label has *an* answer.
Two later-falsified answers passed (r5's coordination claim; r3's "only subprocess
call" adjacency, falsified by r8's nested vendor tree). This is a known workspace
class ("gate can't tell empty from unlooked" — here: can't tell answered from
answered-correctly) and is structural to any self-attestation; the mitigation is the
repair loop in (4), which converts each falsification into a mechanical check.

## Counterfactual cost estimate

Conservatively: catching class A at turn 0 removes ~7 findings and likely folds
rounds 1 and 4 into confirmations; rigorous fix-sweeps (class B) remove ~8 more across
r2/r3/r5/r6/r9; the arms-race rule at its earliest legal firing removes ~2 rounds of
the drift family. A faithful application of the suite **as already written** plausibly
converges this arc in **4–6 rounds instead of 10**; adding the absent classes points
toward 3–4. (Each round ≈ one full serial cycle; the skill's own pricing is 15–30 min
plus a paid review invocation.)

## What was NOT a failure

- The preflight did run before every commit, with named answers; the initial diff's
  hermetic suite, mutation pin, and wiring were first-draft complete enough that no
  round found a missing test file, missing CI wiring, or manifest omission.
- One finding (r5 append-window) was a reviewer misread and was correctly rebutted
  with a measurement-validity argument rather than absorbed as churn.
- The r7 subtraction (pinned worktree) and r10 hold-reversal, once made, ended their
  finding families permanently — the late decisions were the right decisions.
- The 10-round budget refusal worked exactly as B-215 intends (as it did on U-HE-34).

## Checked against the suite's historical learnings (operator follow-up)

The classes are supposed to be *derived from the historical session corpus*, so the
audit was re-run against both derived-learning layers.

**(a) The corpus classifier (`scripts/refresh-classes.py`, run 2026-08-26).** The live
gate log now carries **466 findings matching NO known class** — the ten classes were
distilled at the 2026-08-24 corpus and the re-derivation cadence has not kept up.
Several of THIS arc's findings sit in that unmatched tail (the result-row /
unenforced-live-row family incl. the r10 P1, decide's required-series, the TypeError
envelope shape, the ABA binding, the witness-independence P3): for those, the skill
had genuinely not derived the class from history — an **Absent** verdict against the
skill file, but see (b).

**(b) The memory layer — learnings already distilled from PAST session logs and loaded
at session start.** At least eight of this arc's finding families map onto standing
memory entries that predate the arc:

| This arc's finding family | Pre-existing historical learning (memory index) |
|---|---|
| 8 findings on my own absorption fixes (28%) | `absorption-rounds-introduce-their-own-defects` |
| Guard reps saga (any→1–99→1–9→5–9); drift windows | `every-bound-added-to-fix-a-leak-is-a-new-defect-surface` |
| Drift hardening r2→r7 | `non-convergent-adversarial-hardening-arms-race` |
| Whole-binding after head-only | `fix-reopens-defect-from-opposite-side` |
| Result row with no reader; inert live row (the P1) | `wired-handler-unreachable-two-halves-of-one-mechanism` ("unit-green isn't closeable until a REAL path reaches it — two halves") |
| Overlap witness gap; unwitnessed r8 SIGTERM fix | `witness-must-see-the-mechanism` / `mutation-probe-load-bearing-witness` |
| Four-round pilot-gate hold | `merge-gate-overturns-register-and-hold-fail-closed-guard` |
| RLock signal-safety | sibling of `multiprocess-fork-plus-threading-lock-deadlock` (lock held across an asynchronous control transfer) |
| Sweeps answered-but-wrong passing the gate | `gate-cannot-tell-empty-from-unlooked` |

**Revised conclusion.** The knowledge was NOT missing — it existed in the durable
learning layers before the arc began. The failure is a **broken transfer loop in both
directions**: memory→code (entries are passive prose; none of these had been promoted
down the skill's own mechanization ladder into a class or a grep rule, and passive
knowledge decaying is itself a documented premise of the skill), and corpus→skill
(the 466-finding unmatched tail shows re-derivation has not run at its staleness
trigger, so lessons the memory layer had *narratively* never became classes the
preflight *fires on*). The skill file even predicts this exact failure: "a rule
recorded in memory failed to prevent the same defect days later, in the same arc that
wrote it — so the repair obligation is IN-COMMIT, not remembered." This arc reproduced
that finding at suite scale.

## The full knowledge surface available at authoring time (operator follow-up 2)

The agent's proactive-implementation knowledge is not just the skill + memory. Five
layers were available before the first line of probe code was written:

1. **The skill's ten classes + grep** (audited above — Unfired/Absent per finding).
2. **The memory index** of historically-derived learnings (audited above — 8 families
   pre-existed).
3. **The architectural laws** (loaded at session start; e.g. parse-don't-validate
   covers r1's reps boundary, single-enforcer covers the drift-gate consolidation).
4. **The reviewers' empirical record** — the very gate log the reviews write to,
   queryable BEFORE authoring: "what has this reviewer historically found in code that
   spawns subprocesses / adds guard allows / registers manifest rows?" It was never
   queried pre-authoring in this arc.
5. **The already-reviewed sibling code — the reviewers' standard in executable form.**
   The surfaces the probe consumes carry heavy prior reviewer pressure recorded in the
   same log: `codex_review.py` 32 findings, `review_loop_gate.py` 32,
   `review_wrapper_common.py` 20, `agy_review.py` 6, `round_log_publish.py` 3. Those
   files ARE ~90 absorbed findings' worth of the local bar.

Layer 5 is the sharpest miss this follow-up exposes: **at least 7 of this arc's 29
findings re-derived, round by paid round, disciplines the reviewed siblings already
embodied.** `run_bounded`/`terminate_bounded` already encoded the
process-group-kill and vendor-session facts (r4, r8); `agy_review` already carried
the SIGTERM/TerminationRequested machinery (r8 — the fix was literally importing it),
the moved-HEAD refusal (r2/r7 drift family — I even *cited* it as precedent while
still shipping the weaker check), and strict envelope validation (r7 TypeError);
prior arcs' guard-allow commits (U-HE-25/U-HE-34) modeled the recipe⇒allow⇒witness
pattern (r2). The skill's "precedent search" paragraph mandates reading a surface's
own consumers before writing a new one — but it is scoped to *data* surfaces; nothing
directs it at *mechanism* siblings ("before building X, read how the adjacent
already-reviewed code does X"), and that is where most of the re-derivation cost
landed.

**Answer to the operator's question in one sentence:** yes — the knowledge to
proactively implement to this codebase's and these reviewers' standards was
substantially all present across the five layers before round 1, and the audited
failure is almost entirely an *activation and retrieval* failure (plan-skeleton
deference over spec text; precedent search not applied to mechanism siblings; the
corpus never queried pre-authoring; zero in-commit skill repairs), not a
knowledge-absence failure.

## What the suite is actually scaffolded on (operator follow-up 3, verified at source)

- **`defect-class-preflight` (lever B-211):** scaffolded on `.harness/merge-gate-log.jsonl`
  — the C-HE-24 finding corpus — verified at `.claude/skills/defect-class-preflight/scripts/refresh-classes.py:4,53` (the
  checklist "is a distilled map" of that log; the script re-clusters it live), with
  `evals/evals.json` (+ two fixture sets) as the planted-defect regression harness and
  the skill file's git history as the audit trail.
- **`register-pr-prose` (lever B-212):** distilled from the prose-finding slice of the
  same log.
- **`arc-lever-report`:** observability only — reads `.harness/arc-metrics.jsonl` arc
  rows (round counts, N6 cohorts) to measure whether the two levers are improving arcs.

So yes: the data this audit interrogated IS the suite's own scaffold. This arc
appended 29 fresh findings (plus the live probe's measurement rows) to that exact
substrate — the feedstock arrived — but none of the three distillation steps the
suite defines (re-cluster → class, miss → in-commit skill repair, miss → eval case)
executed during the arc, and the 466-finding unmatched tail shows the re-cluster
trigger has been missed corpus-wide, not just here. Two knowledge layers this audit
found decisive — the memory index and the reviewed-sibling code (~90 absorbed
findings embodied in the wrapper files) — are NOT wired into the scaffold at all;
repairs 1–4 below would bring the first in, and a "mechanism-precedent search" rule
would bring in the second. This arc's 10-round cost will itself land in
`arc-metrics.jsonl` at drain and appear in the B-211 cohort — the lever report is the
standing instrument for watching whether these repairs move the number.

## Ledger-novelty partition (operator follow-up 4)

All 29 findings partitioned by novelty against the suite's ledger (the ten committed
classes + inventory/meta-rules), judged per finding rather than by the crude regex
clusterer. One finding (r5 append-window) was a rebutted reviewer misread and is
excluded; 4 instances are re-presses of one type (the unenforced-gate family) and 3
of another (invented-vs-contract-derived bounds), counted as instances of their type.

**Bucket 1 — type already squarely IN the ledger: 11 of 28 instances (~39%), ~8 types.**
r1 exit-code validity (new-consumer inventory's own crash-aliasing question);
r1/r3/r7 drift TOCTOU family (class 1 verbatim: check-then-act on refs);
r2 composite-compare (class 1 + fix-sweep meta-rule); r3 OSError arm (class 3);
r3 overlap witness + r5 witness-independence + r9 unwitnessed SIGTERM fix (class 4);
r6 registration race (class 1 on my own new shared state); r7 null-envelope
(inventory's first mandated question). Every one an ACTIVATION failure, not a
knowledge gap.

**Bucket 2 — genuinely new type with NO reasonable inference path: 0.**
Strictly none. The two hardest — r8 nested vendor session-group and r10 RLock
signal-reentrancy — sit at the boundary, but both were resolvable from in-repo
sources when pressed (the sibling wrapper's `run_bounded`/`terminate_bounded` source;
the `multiprocess-fork-plus-threading-lock-deadlock` memory's lock-held-across-
asynchronous-control-transfer analog), so they belong at the far edge of bucket 3.

**Bucket 3 — new-to-the-ledger but edge-similar / inferable by deliberate reasoning:
17 of 28 instances (~61%), ~10 distinct types.** Each with its inference bridge:
- Unenforced declared gate (4 instances incl. the r10 P1): class 6's "what call
  sequence reaches this?" generalized from branch to gate, + the two-halves memory.
- Invented-vs-contract-derived bounds (3 instances): mirror-image of class 3's
  suppression-input rider (what an ALLOW admits is spend surface), + the
  every-bound-is-a-new-defect-surface memory.
- Arg-sourced count boundary (r1 P3): class 5 says "unvalidated environment-sourced
  budgets" — a CLI arg is the same shape one token over.
- New command surface ⇒ guard wiring (r2): the spec's own runs_in "operator/loop" +
  the U-HE-25/U-HE-34 precedent commits.
- Durable terminal record (r4): empty-vs-unlooked memory + a spec phrase read at
  grounding.
- Required-set completeness (r4 P3): the contract names {1,2,4} — pure requirements
  reading.
- Process/signal lifecycle family (4 subtypes: group kill r4, run-level cleanup r5,
  nested tree r8, reentrancy r10): class 8's boundary insight recursed one level per
  round, with the sibling wrappers' source embodying every answer, and the r8 case
  being the exact recursion of the r4 question ("I killed my child's group — does my
  child spawn its own?").
- Escape-path unification (r7): classes 3+6 composed.
- Buffered partial-loss (r9): the inventory's mid-crash question turned inward on my
  own writer.

**Net:** the ledger already contained ~39% of the arc's findings outright; the other
~61% were one deliberate analogy, one spec phrase, or one sibling-source read away;
**zero findings were beyond the reach of knowledge + reasoning available at authoring
time.** This is the quantified form of the audit's verdict: the gap is activation and
analogical transfer, not coverage.

## Recommended repairs (proposed, not yet applied — HIL pending)

1. **defect-class-preflight**: add three classes — (i) *spec-phrase-to-code
   completeness*: every quoted contract phrase in a registered row/docstring must name
   the code that discharges it; (ii) *new command surface ⇒ permission-guard wiring +
   witness* (fires on any new justfile recipe whose runs_in includes "loop");
   (iii) *signal/lock safety*: any signal handler + lock combination demands the
   reentrancy question. Add the four greppable shapes to `preflight-grep.sh`.
2. **Sharpen the fix-sweep rule** with this arc's tell: "if your absorption commit
   defines a new class/lock/registry/regex, the ten classes apply to IT as if it were
   turn-0 code — 'no new mechanism' is never a legal answer for a commit that adds
   one."
3. **Bound-derivation rule**: any numeric bound in a guard/allowlist must cite the
   contract value it derives from, never a syntactic convenience.
4. **Hold-policy rule** (promotes the existing memory into the skill): a reviewer
   finding held as "later unit's job" must be accompanied in the SAME round by the
   minimal fail-closed probe, or the hold is presumptively wrong (this arc: 4 rounds).
5. Add the planted-defect eval cases for the two P1 shapes.

*Author: session u-he-35 (Claude), 2026-08-26. Sources: `.harness/merge-gate-log.jsonl`
(arc u-he-35 rows), `.harness/.sweep-answers-u-he-35-r1..r10.md`,
`.harness/tmp/u-he-35-rounds/r*.log`, `.claude/skills/defect-class-preflight/SKILL.md`,
`.harness/spec/Spec_HE_Loop_Lanes_v1.md` §8.1/C-HE-15/C-HE-22, MEMORY.md index.*
