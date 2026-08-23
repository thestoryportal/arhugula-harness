# Session audit — U-HE-29 / PR #1426 (2026-08-22 → 08-23)

**Purpose.** Trace where this session's token and wall-clock cost went, and name the
workflow failures precisely enough that a forward session cannot repeat them. Every
figure below is derived from a named source and reproducible; the commands are cited.

**Sources.** `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/21eda9ac-055c-4c5e-a950-35b4712c12a8.jsonl`
(main transcript + 11 subagent transcripts, `usage` fields); `.harness/merge-gate-log.jsonl`
(973 rows, 105 for `u-he-29`); `.harness/arc-metrics.jsonl`; `git log 0a4ad06bd~1..4fd61068d`;
`gh run list --branch feat/u-he-29-loop-status-shared-venue`; `gh pr view 1426`.

---

## 1. Measured cost

| Metric | Value |
|---|---|
| Model-call span | 2026-08-22T19:10Z → 2026-08-23T07:18Z = **12.1 h** |
| Commits | **53** (feat + 52 absorption/chore) |
| Model calls | **2,149** (1,158 main loop + 991 across 11 subagents) |
| Output tokens | **1,400,705** (1,048,890 main loop) |
| Cache-read tokens | **759,307,518** |
| Cache-write tokens | 6,723,650 |
| Median context per call | **553,023** — max **950,156** |
| Compaction events | **0** |
| Total tool-result bytes | 483,543 chars ≈ **121k tokens** |
| Out-of-family review rounds | **24** (105 findings: 8 P1 / 81 P2 / 16 P3) |
| CI runs on branch | 13 (12 success, 1 cancelled) |
| Lines authored | **3,992** added / 2,229 deleted |
| Lines cut at the end | **1,483 (37% of everything authored)** |
| Final PR | +2,044 / −281, 33 files — **still OPEN, unmerged** |

### 1.1 The cost mechanic — it is not tool output

Tool results across the entire session total ~121k tokens. The context nonetheless ran at a
**553k median and reached 950k**, with **zero compactions in 12 hours**. The growth is
therefore **self-generated**: 1.05M output tokens in the main loop, every one of which
accretes into the input of every subsequent call.

The cost model is approximately:

```
cache_read  ≈  n_calls × (preload_baseline + cumulative_output / 2)
            ≈  1,158  ×  (100k + 1.05M/2)  ≈  624M      [observed: 624,169,311]
```

**Consequence — cost is quadratic in session length, not linear.** Doubling the number of
turns roughly quadruples the token bill. This is the single largest lever available and it
is not addressed anywhere in the current governance.

### 1.2 The split that matters

Round 14 (commit `166dd03f6`, 2026-08-23T01:51Z) recorded that the migration's founding
measurement was **wrong**. Splitting the session at that moment:

| Window | Calls | Output | Cache-read |
|---|---|---|---|
| Before falsification | 818 (38%) | 701,921 | 255,048,701 (34%) |
| **After falsification** | **1,331 (62%)** | **698,784 (50%)** | **504,258,817 (66%)** |

**62% of the session's model calls and 66% of its token volume were spent after the premise
justifying the work had been empirically falsified.** Because of §1.1's quadratic curve, that
post-falsification window is disproportionately expensive: it is 62% of the calls but 66% of
the tokens, and it ran at the most expensive end of the context curve.

---

## 2. Failure trace

Reconstructed from operator turns, skill invocations, and commit timestamps (UTC).

| Time | Event |
|---|---|
| 19:10Z | `/roadmap-continue` — session opens on U-HE-29 |
| 21:16Z | `/roadmap-continue` again |
| ~21:56Z | Review round 1 |
| **r2** | Review raises: the venue move would strand still-open deferrals |
| r2–r13 | Premise accepted; migration built and hardened — atomic claim-by-rename, orphan recovery, pid liveness, NUL enumeration, timestamp staleness, 5-value exit taxonomy, 44 tests |
| 01:34Z | **`/ship-pr` invoked** — the agent believes the arc is done |
| 01:36Z | PR #1426 opened; first CI run |
| 01:43Z | `/merge-gate` invoked |
| **01:51Z** | **r14: the founding measurement is shown to be an ARTIFACT. Live dry-run confirms 0 files to import.** |
| 02:02Z–05:14Z | **Rounds 15–23 harden the machinery anyway.** 4 of the session's 8 P1s land at r19 |
| 03:11Z | Operator: "continue" |
| **05:25Z** | **Operator INTERRUPTS: "requiring many turns and eating up tokens. Assess where implementations are failing."** |
| 05:55Z | Operator: "proceed to merge" |
| **06:36Z** | **Operator INTERRUPTS again: "Find a safe and clean pause point for HIL."** |
| 06:38Z | **CUT** — `b1a099294`, −1,483 lines |
| 07:08Z | `/context-save` + memory reflect |
| — | **PR #1426 never merged** |

**4 hours 47 minutes and ~10 review rounds elapsed between the falsification and the cut,
and the cut happened only because the operator intervened — twice.**

---

## 3. Where the workflow failed

### F1 — There is no agent-side circuit breaker. The only one was the human. *(primary)*

The agent had the falsifying evidence in hand at 01:51Z and wrote it into a commit message.
It then continued absorbing findings for 4.8 h. Nothing in `roadmap-continue`, `ship-pr`,
`merge-gate` or CLAUDE.md §13 causes a re-evaluation of *whether the work should exist*.
Every loop mechanism is a **convergence** mechanism — it drives findings to zero. None is an
**abandonment** mechanism.

The operator's 05:25Z interrupt is the actual control that stopped this. That control is not
in the repo.

### F2 — Absorbing the finding buries the question

The r14 finding was *absorbed as a fix* ("the founding measurement is corrected") rather than
*escalated as a premise event*. Once absorbed, the loop's next step is r15 by construction.
The reflex to fix what the round says is precisely what prevented asking whether the round's
subject should be deleted.

### F3 — `ship-pr` is not a gate; the arc ran 12 more review rounds inside it

`/ship-pr` fired at 01:34Z at round ~12. Rounds 13–24 then ran *after* entering ship mode —
half the session's review rounds occurred inside a phase nominally meant to close it. Entering
the ship gate carried no assertion that would fail on continued churn.

### F4 — The measurement substrate is dark, so cost is invisible in-flight

- `.harness/arc-metrics.jsonl` has **zero rows for the last 6 merged PRs** (#1416, #1417,
  #1418, #1420, #1422, #1424) and none for #1426. Last recorded arc: `pr-1415`. No
  `.harness/arc-metrics-queue/` exists.
- `round_wall_s`, `phases`, `round_outcomes` are **empty in every row that does exist**.
- `merge-gate` emitted **0 rows for `u-he-29`** despite driving ≥6 fix commits. Its last
  emission was `pr-1424` at 2026-08-22T12:26Z.
- **arc_id keyspace is split**: `codex_review_wrapper` writes `u-he-29`; merge-gate lenses
  write `pr-1426`-style ids. Any join between reviewer producers on `arc_id` silently returns
  empty — you cannot compute "what did each lens uniquely catch on this arc."
- `unique_catch` and `disposition` are **null in all 973 rows** of the log. These are the two
  fields B-173's kill condition and U-HE-43's shadow-trial scoring depend on.
- `gemini_review_wrapper` last emitted 2026-08-22T05:07Z — not run this session.

The consequence is concrete: **when the operator asked at 05:25Z where the cost was going,
there was no ledger that could answer.** The audit you are reading had to be reconstructed
from raw transcripts.

### F5 — Subagent fan-out was not free

11 subagents consumed 991 calls / 352k output / 135M cache-read — ~18% of the session's token
volume. They ran during the migration-hardening window, i.e. a meaningful share of the fan-out
was spent reviewing code that was deleted hours later.

---

## 4. The wrong lesson to draw — stated so nobody draws it

**Do not cap review rounds.** The data actively refutes that fix: **all 8 P1 findings landed at
round ≥10, and 7 of the 8 at round ≥14** — i.e. after the falsification, in code that was about
to be deleted (4 at round 19 alone). The late rounds were *productive*. A round cap would have
shipped real P1 defects while leaving the wasted migration in place — the worst of both.

The review loop was not failing. It was working correctly **on code that should not have
existed.** The lever is the premise check, not the round budget. This is consistent with the
standing memory `[[review-loop-yield-is-not-front-loaded-when-inventing]]`.

---

## 5. Preventive actions

Ordered by leverage. Each names a concrete trigger, because a discipline without a trigger is
what F1 already proved insufficient.

### P1 — Premise re-check on falsification *(fixes F1/F2)*

When a review round's finding **falsifies a measurement that justified building something**,
the round is not absorbable until the build-or-cut question is answered in writing. Trigger
phrases in the agent's own output are the detector: "was wrong", "is an artifact", "measured
X but actually", "the founding measurement". Mechanizable as a `tools/mechanized_checks/`
class under U-HE-40 — the check is a scan of the round's own commit message against the
register's stated premise.

### P2 — Machinery-vs-unit round attribution *(fixes F2)*

Per round, attribute findings to *the unit under review* vs *machinery this arc added*. When
the ratio crosses ~2:1 toward self-added machinery for 3 consecutive rounds, halt and surface.
In this session the signal was available from r6 onward and nobody was computing it. This is
one field on the existing C-HE-24 record, not new infrastructure.

### P3 — In-flight cost visibility *(fixes F4 — precondition for everything else)*

The instrumentation to answer "what is this arc costing" exists in schema and is not being
written. Concretely owed:
- Repair arc-metrics capture — 6 consecutive merged arcs recorded nothing. Adjacent to
  **B-175** but distinct: B-175 is about drain durability under concurrency, this is total
  non-emission.
- Unify the `arc_id` keyspace across `codex_review_wrapper` and the merge-gate lenses. **New
  finding — not currently registered.**
- Populate `unique_catch` / `disposition`, null in all 973 rows. **New finding — blocks B-173
  and U-HE-43 from ever scoring.**
- Land **B-171** (round wall-clock) — it is the precondition for P2 and for B-173's kill
  condition, and its absence is why this audit needed transcript archaeology.

### P4 — Session length is a cost variable *(fixes §1.1)*

Cost is quadratic in turns. A 12-hour, 2,149-call, zero-compaction session is the expensive
shape regardless of what it produces. Prefer arc-sized sessions with a clean handoff at the
boundary; when a session passes ~500 calls or ~400k context without an arc closing, that is
itself the signal to checkpoint and cut a fresh context.

### P5 — Entering `ship-pr` should assert something *(fixes F3)*

`/ship-pr` at round 12 followed by 12 more rounds means the gate asserted nothing. Entering it
should record the round count and diff digest; re-entry after N further rounds should surface
rather than proceed silently.

---

## 6. What was already captured, and what this audit adds

The prior session's own reflect pass captured the premise lesson well at
`[[falsified-premise-rescope-dont-keep-hardening]]`, including the semantics-change
measurement trap and the B-198 filing. That memory is accurate and needs no correction.

**This audit adds what that memory does not contain:**
1. The **quadratic cost model** (§1.1) and the fact that context growth is self-generated, not
   tool-driven — no memory covers this.
2. The **62% / 66% post-falsification split** — quantifies "expensive" for the first time.
3. **F1 as a structural gap**, not a judgment lapse: the loop has convergence mechanisms and
   no abandonment mechanism, and the only circuit breaker was the operator.
4. **F4, the dark instrumentation** — including two previously unregistered defects (arc_id
   keyspace split; `unique_catch`/`disposition` never populated).
5. **The explicit anti-lesson** (§4) that a round cap is the wrong fix, with the P1-arrival
   data that refutes it.
