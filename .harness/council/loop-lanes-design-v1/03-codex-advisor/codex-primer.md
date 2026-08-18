# Cold review request — descriptive primer only

You are reviewing a design document COLD. You have not seen any prior review of it, and none is
being shared with you. Form your own independent judgement.

## What the document IS

It is a consolidated engineering design for an autonomous "roadmap loop" in a Python 3.12 workspace
at /Users/robertrhu/Projects/arhugula-v2. The loop today runs ONE unit of work at a time: it picks a
task, builds it in a `git worktree`, opens a PR, gates the PR through CI plus several LLM review
passes, merges to `main`, then commits a mandatory follow-up "terminating refresh" commit.

The operator's fixed requirement is to run **up to 4 of these lanes in parallel**, safely, without
conflicts. That requirement is settled — do not argue for fewer lanes.

The document merges two earlier engineering efforts: one about loop efficiency/gate reliability, one
about parallel worktrees. It proposes a phased build: Phase 0 correctness fixes, Phase 1
measurement/evidence, Phase 2 machinery.

## Hard constraints on any recommendation

- Coordination primitives must be hand-rolled from the **Python standard library plus git**.
  No Temporal/Prefect/Celery/Redis/broker. A recommendation needing a new dependency is not actionable.
- This is workspace tooling, not the product's own runtime architecture.

## What to do

Read the document (path below), then read the actual code it cites in
`/Users/robertrhu/Projects/arhugula-v2` — especially `tools/arc_metrics.py`,
`tools/hooks/permission-guard.sh`, `tools/hooks/loop_lib.sh`, `.claude/skills/two-lane/SKILL.md`,
`.claude/skills/ship-pr/SKILL.md`, `justfile`.

Answer, in your own judgement:
1. Is the phased build order right? What is misordered?
2. Which of its claimed "live defects" (§4, X1-X8) are real, and are any overstated or wrong?
3. What is the single most dangerous thing about this design that the document does not say?
4. Is anything in it internally inconsistent?
5. What would you cut, and what is missing entirely?

Cite `file:line` for anything you assert about the code. Say plainly when you cannot verify something.

---
# THE DOCUMENT
# Harness Loop + Parallel Lanes — Design v1

**Status:** authoritative consolidated source. **Nothing implemented. Repo clean at `17011f89`.**
**Date:** 2026-08-17

**Supersedes as the single current source:**
- `loop-eng-2026-08-16/BUILD-PLAN-operator-ratified-2026-08-17.md` (ratified; carried forward intact)
- `loop-eng-2026-08-16/STAGE7-FINAL-opus-grounded-findings.md`
- `parallel-lanes-2026-08-17/STAGE7-FINAL-opus-grounded-findings.md`
- `parallel-lanes-2026-08-17/STAGE5-opus-integrated-reconciliation.md`

Those remain the evidence record. **This file is what to act from.** Where they conflict, this file
wins; where it is silent, they govern.

**Provenance.** Two full review pipelines (research fan-out → blind out-of-family review →
cross-reviewer debate → reconciliation → 11-voice council → cross-voice debates → adversarial
review). **63 logged corrections** across both arcs (14 loop + 49 lanes), a majority caught by a
layer other than the one that made the claim.

---

## 1. Scope

Two arcs, one system. The **loop** arc asked *why is each arc slow and how do we know a gate ran*.
The **lanes** arc asked *how do we run four of them at once*. They share files, defects, and
sequencing, so they are consolidated here.

**Out of scope:** H_T design surface (this is H_E process/tooling, mode-agnostic), and anything
requiring a framework — coordination is hand-rolled from Python stdlib + git only.

---

## 2. The system in one picture

```
  Lane 1 ┐
  Lane 2 ├─ build in PARALLEL (worktrees, own gates, own reviewers)
  Lane 3 │
  Lane 4 ┘
             ↓  lease-file protocol (CAS, no daemon)
        ┌──────────────┐
        │ MERGE DOOR   │  depth-1 by construction (§12.2.1 fixed point)
        │  1 at a time │  merge → terminating refresh → next
        └──────────────┘
             ↓
            main
```

**Build parallel, land serial.** Already the workspace's committed model at N=2
(`two-lane/SKILL.md:8`: *"Two arcs can be **built** concurrently. They cannot be **landed**
concurrently"*), extended to 4.

**Expected yield: well under 2×, not 4×.** State this explicitly to avoid a scope-expectation
mismatch. Adding lanes 3–4 adds little on top of lane 2 until the re-gate cost is addressed.

---

## 3. Committed decisions

### 3.1 Ratified by the operator (loop arc, 2026-08-17) — carried forward unchanged

| # | Decision |
|---|---|
| D-A | Build through Layer 2 (safety + measurement + speed) |
| D-B | **Extend existing records; do NOT build a new ledger** |
| D-C | Wire the second cross-vendor reviewer as **automatic failover** |
| D-D | Wire the shadow trial into the loop; measure value live |

**L0.2′ (the D-A × D-B reconciliation):** deliver the *function* (one common field set) by
extension, not the *artifact*. `.harness/arc-metrics.jsonl` and a structured sibling to
`.harness/merge-gate-log.md` both emit
`{finding_id, location, observed_evidence, expected_contract, severity, finding_type,
lineage_claim, producer}`. Dropped with the ledger: hash-chain tamper-evidence. Mitigation: never
overwrite a finding row; append a new row with the same `finding_id`.

### 3.2 Decided by the lanes arc

| # | Decision |
|---|---|
| L-1 | **Build parallel, land serial.** Merge door stays depth-1 |
| L-2 | **Lease-file protocol, not a coordinator process.** No daemon, no spawner, no merge-queue lock |
| L-3 | **D1 = (a) strict serial** now — not because alternatives fail, but because the gate that would replace full re-gating is an unreviewed draft |
| L-4 | **Sequence: fix defects → gather evidence → only then build machinery** |
| L-5 | **JSONL stays the durable record.** sqlite rejected — new shared DB+WAL surface, no correctness gain, loses git-diffability |

### 3.3 The binding constraint

`codex_context_guard.py:774` hard-fails `ROADMAP_STATUS_DRIFT` on `main` when two or more content
commits stack past the last verified refresh. **This is mechanical and is why the merge door is
depth-1.** On a lane branch the same mismatch downgrades to a `warn`
(`ROADMAP_STATUS_BRANCH_DIVERGED`, `:808`) — so lanes may build freely; only landing is constrained.

---

## 4. Live defects — not proposals

These exist at HEAD today. Both arcs found them independently.

| # | Defect | Evidence |
|---|---|---|
| **X1** | **An absent verdict can read as clean.** Reviewer CLI exits 0 having produced nothing. Recurred *live* during the review pipeline itself | loop D1; violates already-ratified invariant #5 |
| **X2** | **13.7% of CI runs are CANCELLED** (190/1,390) with no intervention anywhere | loop D2; violates ratified invariant #14 |
| **X3** | **Split-brain ledger.** `LEDGER = REPO/…` is per-worktree (`arc_metrics.py:44-45`); `QUEUE_DIR` is shared outside the repo (`:59-63`) | lanes E6 |
| **X4** | **Duplicate append with ZERO temporal overlap.** A drains → restores the queue entry pending merge → hours later B drains; `committed_arc_ids()` (`:551-581`) sees the arc unmerged, `local` (`:697/:706`) reads B's own ledger, `append()`'s guard (`:408-409`) is per-worktree — **all three pass** | lanes E26, verified |
| **X5** | **ABA takeover + uncaught `FileNotFoundError`.** On the `AbortError` branch nothing is written anywhere, yet the code prints `KEPT QUEUED` and returns `kept += 1` — **actively false** | lanes E5/E9/E41 |
| **X6** | **Loop-marker venue split.** `hook_project_dir()` = `${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}` resolves per-worktree in a raw shell, hook-injected in a hook — the same marker is two different files | lanes E10, probed |
| **X7** | **Docker collision.** `compose.yaml:1` hardcodes the project name + ports `3200/4317/4318`; `justfile:471` passes no `-p`. A later lane can restart lane A's containers | lanes E47 |
| **X8** | **`codex-review` has no fail-closed wrapper.** `tools/codex_review.py` does not exist; Gemini routes through the hardened `agy_review.py`. Asymmetric silent-failure exposure | lanes E35 |

**X1 and X8 are the same defect from two directions.** X4 is the primary lanes defect and **cannot
be fixed by a lock or by flock** — flock dies with the process; this race spans two process
lifetimes and a PR merge.

---

## 5. Build order

### Phase 0 — correctness. Ungated by lane count.

**From the loop arc (ratified):**
1. **L0.1 completion-validity + terminal state.** Verdict counts only if it parses to the expected
   shape; **exit code is never a completion signal**. Permanent (auth) vs transient split; permanent
   skips the retry budget. `REVIEWER_UNAVAILABLE` = BLOCK-equivalent, never APPROVE-able. Failover
   (D-C) held to the **identical** validity bar. CI terminal states `{SUCCESS, FAILURE, CANCELLED}`;
   **CANCELLED is INCOMPLETE, never green.** Routes to the existing durable HITL queue, TTL 24h.
2. **L0.2′ record extension** + pre-register `arc_type` at arc **open** (today it is declared at
   close, so labels are hindsight).
   **→ MUST carry `lane_id` from the start.** It was recommended in the lanes research and **dropped
   from the ratified plan** (`grep -c lane_id` → 0). One field now vs a migration later, on exactly
   the two files X3/X4 implicate.
3. **Give `codex-review` a fail-closed wrapper** mirroring `agy_review.py` (closes X1 + X8).

**From the lanes arc:**
4. **PR-tagged reservation** in `QUEUE_DIR` — the fix for X4. Not in `_claim` (different lifetimes:
   `_claim` dies when `_claim_arc` returns; the reservation must survive review latency).
   `{lane_id, branch, pr: null, reserved_at, pid, host}`; `pr` back-filled by ship-pr; `branch` as
   fallback key. Release on confirmed merge, reclaim on confirmed abandonment.
   **`gh` unreachable → leave untouched** — both guesses are wrong in opposite directions.
5. **flock across the full claim lifetime** (closes X5's exception branch — only this makes it
   unreachable). **Lock file collocated with `QUEUE_DIR`, never under `REPO`** — the natural
   implementation re-creates the exact per-worktree mistake that causes X3.
6. **Lock scoping** — `committed_arc_ids()`'s `git show` (`:571`) outside the critical section, or
   one wedged lane blocks all four.
7. **Split `loop_status.md` by kind, not by lane** (fixes X6 without causing duplicate work).
   Control markers per-lane; `DEFERRED-HIL`/`RESOLVED-HIL` globally visible, reduced by
   `(item-id) → max timestamp`, **no ACTIVATE reset** (`loop_lib.sh:127` scopes the skip-set "SINCE
   the last ACTIVATE", so a sibling's ACTIVATE would wipe an open deferral).
8. **Environment isolation** — Docker per-lane `-p` + ports (X7); `gc.auto 0` per lane; git
   ref-lock retry-with-backoff.
9. **Detections** — split-brain CI check (`jq '.arc_id' | sort | uniq -d` must be empty on every
   merge); post-merge assert merge commit's **first parent** == verified base.

### Phase 1 — measurement and evidence. Gates everything after.

10. **L1.1 phase timing** — queue/execute/capture/absorb/edit/verify as explicit start+end pairs;
    `result_capture` fires on **both** process-exit and log-write-completion, recorded separately.
    **Hard rule: never derive phase timing from inter-record deltas.**
11. **O1** — instrumented 4-worktree `hook_project_dir()` probe. The counterfactual that decides
    whether Phase 2 machinery is needed at all.
12. **O3** — `git merge-tree --write-tree` (verified present, git 2.39.5) over the 172 historical
    colliding pairs → the real conflict rate vs the **38.7% upper bound**. Report semantic-conflict
    rate as **unmeasured, not zero**.
13. **≥3 manual pilot runs at 3–4 lanes with zero new machinery** — satisfies the workspace's own
    gate (`two-lane/SKILL.md:140-142`) and the counterfactual demand with one experiment.
14. **Probe reviewer concurrency** at 2 and 4 simultaneous calls against the single-identity logins.

### Phase 2 — speed and machinery. Only against named, repeated friction.

15. **L2.1 mechanize defect classes**, tagged `deterministic | hybrid | model-judge`. 2 of ~7 are
    mutation-probe-backed and will not be sub-second — do not ship them under a "low-risk" label.
16. **L2.2 remove duplicated executions** — equivalence proved by a party decorrelated from the
    agent whose diff benefits, or by a deterministic execution-context diff. Log the proof.
17. **L2.3 close the local/CI gap** (~58s measured). `codex-context-guard` has no local equivalent.
18. **Lease-file protocol** — widen the existing per-arc CAS; one lease for the merge door itself.
19. **D-D shadow trial**, off the blocking path. Kill after 15 scored rounds if the second
    reviewer's unique-catch count is indistinguishable from zero, judged by an adjudicator of
    neither family. **Wall-clock is explicitly not a kill criterion.**

### Blocked

20. **Local base CAS** (`git merge-tree` recompute + non-force `PATCH /git/refs`) — **Class-3
    blocked.** The workspace merges `--squash`; a locally-built squash commit has one parent and does
    not contain the PR head as an ancestor, so GitHub's ancestry-based auto-close will not fire, and
    `ship-pr/SKILL.md:191` hard-aborts on anything but `MERGED` → ghost PRs, phantom in-flight rows,
    branch hygiene violated. Resolve the merge mechanism and verify on a disposable fork first.
21. **Integration-lens gate** — after its contract survives the same review this arc ran.

---

## 6. Acceptance criteria

| AC | Statement | Status |
|---|---|---|
| 1 | 4 lanes safe and durable | Achievable as build-parallel/land-serial |
| **2** | **Rewritten** — see below | Original was wrong two independent ways |
| 3 | No data loss in shared `.harness/` artifacts | Open — needs Phase 0 items 4–6 |
| 4 | §12.2.1 refresh fixed point preserved | Held — strict serial; **never fold other files into the refresh** (`roadmap_status_refresh.py:1138` enforces one-file shape) |
| 5 | Invariant #16 adjudicated | **Void** — U-WT-09 has 0 matches on `main`; never adopted. No back-flow needed |
| 6 | Decorrelation not weakened | Contract drafted; must route through `just codex-review` on the merge-tree diff, **not** another Claude subagent — otherwise "fresh" buys currency, not vendor decorrelation |
| 7 | No flat round cap | Unaddressed, not violated |
| 8 | Rebase tax addressed or priced | Reframed — the premise for dissolving it collapsed (§8) |
| 9 | Failure mode inventory with detections | 19 named, ~0 detections; three cheap ones specified |
| **10** | **NEW — value.** Cohort comparison of lane-count as a lever | Missing; no baseline exists (two-lane never run) |

**AC#2, restated:**

> For every `arc_id`, across any number of lanes **and any elapsed time between their drains**,
> exactly one row ever reaches merged history, and no queue entry is released before its row is
> durably committed. Two mandatory probes, each required to go RED against the unfixed guard it
> targets and GREEN after the fix, confirmed via `just mutation-probe`:
> **(a) same-instant** — barrier-gated in-process thread sweep enumerating reachable interleavings of
> the claim/takeover critical section across ≥2 simulated lanes (separate `REPO`/`LEDGER`, shared
> `QUEUE_DIR`), asserted over the **union** of all lane ledgers.
> **(b) cross-latency** — sequential, no concurrency: A drains and restores its entry pending merge;
> B drains the same queue while A's row is unmerged; B must not re-append; the reservation releases
> on confirmed merge and reclaims on confirmed abandonment.

Probe (b) is **automatically RED against unfixed HEAD with no fault injection** — a fresh `tmp_path`
has no `origin/main`, so `committed_arc_ids()` returns `set()` through the real code path.

---

## 7. Failure modes (19) — detection status

Required six: split-brain ledger · claim race · orphaned worktree · stale lock · partial merge ·
refresh collision.

Added by review: base TOCTOU (`--match-head-commit` does not pin `main`) · duplicate scheduling ·
stale evidence reuse · **semantic conflict across textually disjoint files** · fragment
double-apply/loss · remote merge succeeded but response lost (reconcile by SHA, never blind retry) ·
merge-queue starvation · **cross-lane loop-marker interference** · shared runtime resources ·
orphaned descendant processes · journal partial write · same register unit changed by two lanes ·
detached `git gc` (live on git 2.39.5 — `gc.autoDetach` predates 2.47).

**By the bar of "an emitted, queryable signal with a stable shape," effectively zero have a
detection today.** Naming is not detection. Phase 0 item 9 plus `lane_id` are the minimum.

---

## 8. The correction that reframed both arcs

The lanes arc originally proposed dissolving the re-gate tax by binding evidence to
`(base_sha, head_sha, prospective_merge_tree_sha, gate-input digests)`.

**Its justifying precedent does not exist.** `.agents/` is the Codex-CLI projection tree, not the
Claude-side contract. Verified: `.claude/skills/merge-gate/SKILL.md` → **0** matches for the
change-class exemption; `--match-head-commit` → in **no** file under `.claude/`, `tools/`,
`justfile`. The real rule is stricter — `two-lane/SKILL.md:78-81`: *"Gate approvals, reviews, and CI
are branch-and-HEAD-bound evidence."*

**What survives:** advancing `main` does not change a PR head; only a rebase does (git mechanics).
**What falls:** "therefore the tax is avoidable" — its only affirmative evidence that relaxing
head-binding is *safe* was that citation. *"Policy, not physical law"* is true and nearly vacuous.
**Whether the alternative policy is safe is open.**

A log-only commit is **structurally verifiable as inert**; a rebase is not — the diff can be
byte-identical while the tree the code executes in has changed. That is exactly where semantic
conflict lives.

---

## 9. Open decisions for the operator

| # | Decision |
|---|---|
| 1 | **Is `gemini-review` a failover for Claude-authored diffs, or is the mandatory chain deliberately single-vendor?** (blocks the loop failover work) |
| 2 | **Escalation TTL** for a CI-blocking gate vs the standing HITL default (24h proposed, not separately ratified) |
| 3 | **Does the ≥3-pilot gate apply** to a top-down N=4 mandate? If O1 shows N-copies is unsafe, the bar would require knowingly running the unsafe configuration three more times |
| 4 | **Gate-coalescing rule** — when ≥2 lanes need you in the same window, one batched prompt or N sequential? The 3–5 lane ceiling maps onto **interruption rate**, not review volume |
| 5 | **Branch protection on `main`** — currently **none** (verified twice: `protected: false`, rulesets `[]`). Minimal protection is a cheap partial base fence, but it is a posture change |

---

## 10. Explicitly NOT being built

- A coordinator **process** / daemon / spawner — L-2
- A merge-queue lock — the door is structurally depth-1; a lock is ceremony
- A new hash-chained ledger — superseded by D-B
- `merge=union` — git concedes arbitrary line order; `.gitattributes:2-4` ties LF forcing to
  hash-chain determinism
- Per-lane `UV_CACHE_DIR` — uv documents its cache concurrency-safe
- An eval-harness / model-judge **as a governance gate** — standing workspace refusal
- Optimistic stale-base merge (D1(c)) — abandons combination-testing; rejected by every reviewer

---

## 11. Evidence standards this design was held to

Carry these into implementation:

- **Byte-check every reviewer output.** Both CLIs exit 0 on total failure. One run fabricated four
  findings while executing **zero** tools; another asserted a symbol didn't exist that lives in code
  and two tests.
- **Ground every cite at session time**, and check the **carrier** — `.agents/` vs `.claude/` drift
  caused the single largest error in either arc.
- **Consensus is where scrutiny is weakest.** Two reviewers reading one brief is not independent
  confirmation.
- **A probe that cannot go RED first proves nothing.**
