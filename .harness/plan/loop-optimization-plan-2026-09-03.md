# Code Implementation Loop Optimization Plan

> **For agentic workers:** each task is one arc through this workspace's loop: `roadmap-continue` picks it from the forward-register row Task 9 creates, the arc lands through `ship-pr` (Codex round, CI, merge-gate for code-touching diffs, door, refresh). Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **What this document is.** A design: for each task, the interface, the test file (the tests are the specification), and a **Design constraints** list. It is not landing code. The task's own arc writes the implementation against the tests and constraints here and carries the reviewer of record for it — five codex rounds on the registration PR (b-230-register; §"Review trail") showed that carrying draft implementations in the plan draws code-level review of code that will be rewritten anyway, at eight findings a round with no convergence. Every finding from those rounds survives below as a constraint.

**Goal:** Cut the wall-clock and token cost of one landed unit (continue → refresh merge) without weakening any gate that has caught a real defect.

**Architecture:** Six cost categories were surfaced by the Archify diagrams at `docs/diagrams/code-loop/`. Grounding on 2026-09-03 sorted them into workspace-ops changes (CI workflow, hooks, just recipes, skill procedure) that land as ordinary PRs, and spec-governed changes (C-HE-06 / C-HE-07 / C-HE-34 in `.harness/spec/Spec_HE_Loop_Lanes_v1.md`, cleared v1.7 on 2026-09-02) that need a spec leg plus a clearance marker before any code moves. Tasks are ordered by measured value over cost. Every task carries the witness that proves its saving against the baseline in §0.

**Tech Stack:** GitHub Actions (`.github/workflows/ci.yml`), bash hooks under `tools/hooks/`, `justfile` recipes, Python 3.12 tools under `tools/`, the merge-gate and ship-pr skills under `.claude/skills/` (and the Codex-runner carrier of ship-pr at `.agents/skills/ship-pr/SKILL.md`).

## Global Constraints

- Posture is mode-agnostic for Tasks 0–5 and for Task 6 Steps 1–5 (they touch `.github/`, `tools/`, `justfile`, `.claude/skills/`, `.agents/skills/`). Task 6 Step 6 (running fewer lenses), Task 7 and Task 8 change what `.harness/spec/Spec_HE_Loop_Lanes_v1.md` guarantees — C-HE-34 ("No collapsing of review layers", `Spec_HE_Loop_Lanes_v1.md:823`), C-HE-06 §4 and C-HE-07 §1, C-HE-06 invariants — and need a version bump, a change note, a clearance marker under `.harness/clearance/`, and the HE plan update, before any skill or code change lands. An operator answer alone does not authorize them; it authorizes opening the spec leg. Spec versions are allocated serially at the moment a leg opens (the next number after the cleared head at that time; v1.8 while v1.7 is the head), never pre-assigned here, since Tasks 6, 7 and 8 may each be accepted.
- The fixed merge string `gh pr merge <pr> --squash --match-head-commit <head_sha>` (`Spec_HE_Loop_Lanes_v1.md:294`, `tools/merge_door.py:896`) may not change in any workspace-ops task.
- The lease is never released while the merge SHA's own `main` run or the terminating refresh is unconfirmed (`Spec_HE_Loop_Lanes_v1.md:321`). No workspace-ops task may release earlier.
- Gate rows are committed before merge and CI must be green at that final head (`.claude/skills/merge-gate/SKILL.md:229-237`). Task 1 makes that CI run cheap; it does not remove it.
- Branch deletion requires an explicit per-instance human approval, loop mode included (`.claude/skills/ship-pr/SKILL.md:471-480`; deny rule at `tools/hooks/permission-guard.sh:618`). Task 4 reduces the number of prompts, not the requirement. The raw `gh pr merge … --delete-branch` and `gh pr close … --delete-branch` verbs stay denied by the guard under every task (`tools/hooks/test_permission_guard.sh:174,279` unchanged).
- Every merged PR is a normal arc: Codex round, CI, merge-gate for code-touching diffs, door, refresh.
- All required status checks on `main` (12 contexts, `strict: true`) must keep reporting a conclusion on every PR. GitHub's docs state "A job that is skipped will report its status as 'Success'. It will not prevent a pull request from merging, even if it is a required check" (docs.github.com, Using conditions to control job execution); a job that never starts, as with a workflow-level `paths:` filter, leaves the check "Expected" and blocks the merge. Task 1 relies on job-level `if:` for exactly this reason and never uses workflow-level `paths:`.
- Two carriers of the ship-pr procedure exist — `.claude/skills/ship-pr/SKILL.md` (Claude) and `.agents/skills/ship-pr/SKILL.md` (the Codex runner). A task that changes the procedure (Tasks 3, 4) changes both and adds a parity witness in the shape of `tools/test_codex_workflow_parity.py`; the merge-gate skill has one carrier (`.agents/skills/merge-gate/` holds no `SKILL.md`).
- Every new `tools/test_*.py` is added to the list in `tools/codex-parity-check.sh` in the same commit — the `tools/` coverage guard rejects any unexecuted module — and inserts its own directory on `sys.path` before importing a sibling (`tools/test_arc_metrics.py:22` shape; the suite runs `--import-mode=importlib`, `pyproject.toml:383`).

---

## §0 Baseline (measured 2026-09-03, re-measure before and after each task)

| Measure | Value | How measured |
|---|---|---|
| CI wall clock, `main` push run 33729280509 | 455 s; pytest job 450 s, coverage 288 s, every other job ≤ 51 s | `gh run view <id> --json jobs` |
| Required checks on `main` | 12 blocking contexts, `strict: true` | `gh api repos/{owner}/{repo}/branches/main/protection` |
| CI runs per landed code unit | 5: PR head, PR final head after gate rows, main on merge SHA, refresh PR, main on refresh merge | ship-pr skill + `tools/merge_door.py:1286-1577` |
| CI path filtering today | none in `ci.yml:33-40`; only `x-al-3-guard.yml:6-8` filters | grounding |
| Lease-acquire budget-exhausted events | 2 door rows (`finding` / `HITL-recoverable` from `merge-door-lease-acquire`) across 76 arcs at the Task 0 final head (both on `u-he-32-refresh2`, a door-only arc; 74 of the 76 arcs had a review round); in-budget yields are not logged (`tools/merge_door.py:1965`) | `loop_cost_baseline.py` → `lease_acquire_events`, `arcs` |
| Review rounds per arc | median 7, max 24 over the 74 reviewed arcs (rounds are head-bound and scoped per review producer — codex rounds, gemini rounds, gate passes with a pass being the per-lens rank at a head; 4 gemini rounds are `failover_ambiguous_rounds`, the possible overcount from the missing failover marker, B-231); the Codex wrapper wrote 1765 and the three lenses 310 of 2585 rows at the Task 0 final head (the pre-registration measurement read median 7 and 2039 of 2455 rows: it counted finding rows only, did not scope rounds per channel, and counted the absorber's adjudication rows as the wrapper's; the log also grows with every review round, so re-run the script rather than restate a figure) | `loop_cost_baseline.py` → `rounds_per_arc_median`, `rounds_per_arc_max`, `codex_rows` (rows the wrapper WROTE — finding / no_finding / reviewer_unavailable — not the absorber's adjudication rows that keep its producer), `rows` |
| Gate rounds with findings | 49; in 35 of them exactly one lens raised findings (head-bound passes with per-lens round ranks, at the Task 0 final head; the pre-registration script read 48 / 33 because it grouped lens rows by `round_n` alone and merged two single-lens passes on different heads of u-he-47 into one) | `loop_cost_baseline.py` → `gate_rounds_with_findings`, `single_lens_rounds` |
| Unique catches by lens | raw `unique_catch` flags: witness-adequacy 22, spec-conformance 10, concurrency 1 (of 88 concurrency findings). Net of `disposition: rejected` adjudications: 19 / 10 / 0 (codex r1 on b-230-register, head `02f656c72`). The contract-valid figure — a flag counts only when the finding's LAST disposition is `accepted` (C-HE-29; the envelope at `Spec_HE_Loop_Lanes_v1.md:632` allows `accepted / rejected / suppressed`, and an unadjudicated flag is not a catch) — — measured by Task 0 at the b-230-task-0 r1-absorption head over 2585 rows / 76 arcs: **witness-adequacy 19, spec-conformance 10, concurrency 0** (33 distinct raw flags, 4 whose last-appended disposition is rejected, 0 unadjudicated) | `uv run python tools/loop_cost_baseline.py` (reports raw, rejected/suppressed, unadjudicated, accepted) |
| Per-call hook cost | `post-merge-refresh.sh:45`, `precmd-clear-cache.sh:28`, `rtk-shape-guard.sh:69` exit within one grep of an ordinary Bash call; `permission-guard.sh:67` exits unless loop mode | grounding |
| Prompt hook signal | `[roadmap] next=?` on every prompt this session (`prompt-context.sh:57` prints `?` when `hook_roadmap_next` returns empty, `tools/hooks/lib.sh:267-286`) | observed |
| Branch-hygiene deferrals waiting on the operator | 3 plus one TTL re-surface in the session banner | observed |
| CI wall clock after Task 1 — content-merge `main` run 33778938360 (the #1503 squash touched `ci.yml`, so the self-guard forced a full run) | 464 s; `changes` 11 s; nothing skipped | `gh run view 33778938360 --json jobs` |
| CI wall clock after Task 1 — refresh-merge `main` run 33780380581 (#1504) | 55 s against the 455 s baseline row above; `changes` 13 s; pytest / coverage / axis-isolation / pyright / tools-coverage `skipped` | `gh run view 33780380581 --json jobs` |
| Required checks on `main` after Task 1 | the live list still has 12 `— blocking` contexts; `main_protection.py verify` derives 14 — missing `merge-gate log consistency (C-HE-23 §2 reducer) — blocking` (new in Task 1) and `split-brain ledger backstop — blocking` (absent before Task 1 too). `just main-protection-apply` closes the gap; it is an outward-facing branch-protection write, surfaced once here and not run from an unattended lane | `uv run python tools/main_protection.py verify` at `8c014d67f` (b-230-task-3) |
| CI wall clock after Task 3 — content-merge `main` run 33789535987 (the #1505 squash touched `ci.yml`, so the self-guard forced a full run) | 538 s (18:16:43Z → 18:25:41Z); nothing skipped | `gh run view 33789535987 --json jobs` |
| CI wall clock after Task 3 — refresh-merge `main` run 33791027069 (#1506) | 52 s (18:31:40Z → 18:32:32Z); pytest / coverage / pyright / tools-coverage / axis-isolation `skipped` | `gh run view 33791027069 --json jobs` |
| Loop cost baseline at `a9173dc8d` (main after #1506; the b-230-task-4 branch point, before this arc's review rounds) | 2599 rows / 78 arcs (76 reviewed); median 6.5, max 24; gate rounds with findings 50, single-lens 36; accepted-only unique catches witness-adequacy 20 / spec-conformance 10 / concurrency 0 (raw 34; rejected-or-suppressed 4; unadjudicated 0); lease-acquire events 2 | `uv run python tools/loop_cost_baseline.py` |
| Branch-hygiene deferrals at Task 4's first live batch | 8 items / 16 branches presented by the reducer (the "3" row above was the count when the plan was written); 8 of the 16 branches were ALREADY absent on origin (an earlier interactive session ran the guarded block but never resolved the rows), so `just branch-hygiene-resolve` cleared those 4 items on its first run; the remaining 4 items / 8 branches are the one atomic push awaiting the operator | `just branch-hygiene-pending`, `just branch-hygiene-resolve` at the Task 4 arc |
| Loop cost baseline at `8c014d67f` (b-230-task-3, before this arc's review rounds) | 2593 rows / 77 arcs (75 reviewed); median 7, max 24; gate rounds with findings 50, single-lens 36; accepted-only unique catches witness-adequacy 20 / spec-conformance 10 / concurrency 0 (raw 34; rejected-or-suppressed 4; unadjudicated 0); lease-acquire events 2 | `uv run python tools/loop_cost_baseline.py` |

The hooks category collapses to two defects (the empty `next=` token and duplicated banner lines); the per-call hooks are already cheap. The serialization category collapses to lease *duration* until Task 8 Step 1 makes in-budget contention measurable; only two hour-long stalls are on record across the 76 arcs at the Task 0 head.

---

### Task 0: Baseline script

**Files:** create `tools/loop_cost_baseline.py`; test `tools/test_loop_cost_baseline.py`; wire the test into `tools/codex-parity-check.sh`.

**Interface.** `python tools/loop_cost_baseline.py [--log PATH] [--loop-status PATH]` prints one JSON object: `rows`, `arcs`, `rounds_per_arc_median`, `gate_rounds_with_findings`, `single_lens_rounds`, `unique_catch_by_producer` (accepted only), `unique_catch_raw`, `unique_catch_rejected_or_suppressed`, `unique_catch_unadjudicated`, `lease_acquire_events`, and — once Task 8 Step 1 lands — `lease_held_yields` and `lease_held_yields_30d_max` from `--loop-status`. Read-only; exit 0.

**Design constraints** (each a reviewer finding on b-230-register unless marked otherwise):
- A round is a distinct `(channel, head_sha, round_n)` per arc named by ANY record kind — head-bound, because `round_n` is reused across an arc's review heads (branch-he-lanes-s1 carries codex round 0 on six heads), and a gate lens mints its own `round_n` independently (PR 1414 recorded one three-lens pass as concurrency r3 beside spec/witness r2), so a gate pass at a head is the per-lens RANK of the lens's `round_n` there: the k-th distinct round of each lens at one head is pass k, lenses at the same rank are one pass (codex r3, r4 on b-230-task-0) — (`finding`, `no_finding`, `finding_adjudication`, `reviewer_unavailable`), over the review producers only — `codex_review_wrapper` and `gemini_review_wrapper` each scoped per producer, a gemini row always its own round: the C-HE-17 D-C failover child is forced to the primary's round number but the log carries no failover marker, so lineage cannot be inferred from key coincidence (tried at r6, reversed at r7 of b-230-task-0); `failover_ambiguous_rounds` reports the keys carrying both a codex `reviewer_unavailable` row and a gemini row as the overcount's upper bound, and the wrapper-side marker is forward work (B-231) and the merge gate (three lenses, passes identified by rank as above). A row the gate emitter writes about itself under a lens's producer (the markdown-sibling write failure, `finding_type: transient-retry`, `lineage_claim: wrapper`, `tools/merge_gate_log.py:300-316`) and Task 6's typed detector-skip row (`no_finding` with `finding_type: lens_skipped`) are not lens work and count in no gate figure (codex r5, r7 on b-230-task-0); the LAST finding row of a `finding_id` lineage carries the `unique_catch` flag that counts, since a retry may re-emit the id with a different value (codex r5 on b-230-task-0). Round numbers are scoped per channel: codex r1 and gate pass 1 are two rounds (u-he-35: 10 + 3 = 13). A clean round and a clean-only arc count; `reviewer_concurrency_probe` rows (an iteration index) and door rows (`round_n: null`) are not rounds. (r1; codex r2 on b-230-task-0)
- A `unique_catch` flag counts only when the finding's LAST `finding_adjudication` row — last in APPEND order, C-HE-24 §5's reducer rule ("readers reduce by `finding_id` → last row"), never by `ts` — carries `disposition: accepted`; `rejected`, `suppressed`, and no adjudication at all are each reported in their own counter, never folded into the catch; catches are counted per distinct `finding_id` (a same-core retry repeats the id). (r1, r5; C-HE-29, C-HE-24 §5, the envelope at `Spec_HE_Loop_Lanes_v1.md:632`; codex r1 on b-230-task-0)
- The `merge-door-lease-acquire` producer is counted from `record_kind: finding` rows with `finding_type: HITL-recoverable` — the shape the door actually writes (the u-he-36 row carried in this PR is one).
- `--loop-status` counts `NOTIFY` rows whose cause is exactly `merge-door-lease-acquire:lease_held_yield` (Task 8).

- [x] **Step 1: Write the failing test**

```python
# tools/test_loop_cost_baseline.py
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def _run(log):
    return json.loads(subprocess.run([sys.executable, "tools/loop_cost_baseline.py", "--log", str(log)], capture_output=True, text=True, check=True).stdout)

def test_baseline_reports_expected_keys(tmp_path):
    log = tmp_path / "log.jsonl"
    rows = [
        {"record_kind": "finding", "arc_id": "a", "round_n": 1, "producer": "codex_review_wrapper", "finding_id": "c1", "unique_catch": False},
        {"record_kind": "finding", "arc_id": "a", "round_n": 2, "producer": "merge-gate-witness-adequacy", "finding_id": "w1", "unique_catch": True},
        {"record_kind": "finding_adjudication", "arc_id": "a", "round_n": 2, "finding_id": "w1", "disposition": "accepted", "ts": "2026-09-03T10:00:00Z"},
        {"record_kind": "finding", "arc_id": "a", "round_n": 2, "producer": "merge-gate-spec-conformance", "finding_id": "s1", "unique_catch": True},
        {"record_kind": "finding_adjudication", "arc_id": "a", "round_n": 2, "finding_id": "s1", "disposition": "accepted", "ts": "2026-09-03T10:00:00Z"},
        {"record_kind": "finding_adjudication", "arc_id": "a", "round_n": 2, "finding_id": "s1", "disposition": "rejected", "ts": "2026-09-03T10:00:01Z"},
        {"record_kind": "finding", "arc_id": "a", "round_n": 2, "producer": "merge-gate-concurrency", "finding_id": "k1", "unique_catch": True},
        {"record_kind": "no_finding", "arc_id": "a", "round_n": 3, "producer": "merge-gate-concurrency"},
        {"record_kind": "finding", "finding_type": "HITL-recoverable", "arc_id": "a", "round_n": None, "producer": "merge-door-lease-acquire"},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    data = _run(log)
    assert data["rows"] == 9
    assert data["arcs"] == 1
    assert data["rounds_per_arc_median"] == 3            # the clean round 3 counts; the door row (round_n null) does not
    assert data["gate_rounds_with_findings"] == 1
    assert data["single_lens_rounds"] == 0               # round 2 had three lenses
    assert data["unique_catch_raw"] == 3
    assert data["unique_catch_by_producer"] == {"merge-gate-witness-adequacy": 1}   # s1's LAST disposition is rejected; k1 is unadjudicated
    assert data["unique_catch_rejected_or_suppressed"] == 1
    assert data["unique_catch_unadjudicated"] == 1
    assert data["lease_acquire_events"] == 1
```

- [x] **Step 2: Run it to verify it fails** — `uv run pytest tools/test_loop_cost_baseline.py -v`; expected: FAIL, script not found.
- [x] **Step 3: Write the script** to the interface and constraints above.
- [x] **Step 4: Run the test, then the script on the real log** — `uv run pytest tools/test_loop_cost_baseline.py -v && uv run python tools/loop_cost_baseline.py`. Expected: PASS; on the real log `lease_acquire_events` is 2 and the accepted-only `unique_catch_by_producer` is recorded in §0 beside the raw and net-of-rejected figures. `gate_rounds_with_findings` / `single_lens_rounds` came out 49 / 35 against the pre-registration 48 / 33 — recorded in §0 with the cause (head-bound grouping), per the rule that a difference from a recorded figure is a finding to record, not to explain away.
- [x] **Step 5: Wire the test into CI parity and commit** — add `tools/test_loop_cost_baseline.py` to `tools/codex-parity-check.sh`; `git commit -m "feat(tools): loop_cost_baseline — measured basis for the loop optimization plan"`.

---

### Task 1: CI bookkeeping fast path (largest saving, workspace-ops)

Two of the five CI runs per unit verify a diff that is only `.harness/roadmap_status.md` (the refresh PR and the refresh-merge push); a third, the gate-rows head, is only the two gate-log files but a `pull_request` diff spans the whole PR (see Step 8). Skip the heavy jobs on those diffs at the job level so the required checks still report.

**Files:** create `tools/ci_bookkeeping_diff.py`; test `tools/test_ci_bookkeeping_filter.py` (wired into `tools/codex-parity-check.sh`); modify `.github/workflows/ci.yml:33-40` (triggers stay), add a `changes` job before line 56 and a light `gate-log-consistency` job, add `needs: changes` + `if:` to the `test`, `coverage`, `axis-isolation`, `typecheck`, and `tools-test-coverage-and-codex-loop` jobs.

**Interface.** `python3 tools/ci_bookkeeping_diff.py <base-sha> <head-sha>` prints `bookkeeping=true` when every changed path is in `{.harness/roadmap_status.md, .harness/merge-gate-log.jsonl, .harness/merge-gate-log.md}`, else `bookkeeping=false`; exit 0 either way; exit 2 on an empty diff (fail loud, never silently skip). `classify(paths: list[str]) -> bool` raises `ValueError` on an empty list. Stdlib only: the `changes` job has no `uv` setup on purpose and must finish in seconds.

**Design constraints:**
- The `changes` job's checkout uses the SHA every other job in `ci.yml` pins (`actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4`, `ci.yml:61,93,121`): this job decides whether five heavy checks run, so a movable tag here is a bypass. (r2)
- Every gated job carries `needs: changes` and `if: always() && needs.changes.outputs.bookkeeping != 'true'`. `always()` is load-bearing: without it a failing classifier marks every dependent job `skipped`, GitHub reports them as Success, and a broken classifier makes pytest disappear from a mergeable PR; with it a failed classifier leaves the output empty and every heavy job runs.
- `lint`, `codex-context-guard`, `arc-ledger`, `substitution-ledger`, `claude-md-citations`, `semantic-overlay`, `q1-review-gate`, `q3-evidence-and-closure-gate`, `split-brain`, `clearance-corpus` stay unconditional: together under a minute, and `codex-context-guard` is the check a status-only PR exists to pass.
- The fast path skips pytest (which runs `tools/test_merge_gate_log.py`) on exactly the commits that append gate rows, and no unconditional job today runs the JSONL↔Markdown consistency reducer (`rg merge-gate-log .github/workflows/ci.yml` is empty). Add an unconditional `gate-log-consistency` job so a sibling mismatch cannot receive green final-head CI. `merge_gate_log.py` is NOT stdlib-only — its siblings `finding_record` and `review_wrapper_common` import the declared `jsonschema` dependency — so the job installs the project (the same `uv sync` step the light `lint` job uses) and runs `uv run python tools/merge_gate_log.py check`; a no-setup `python3` invocation would fail at import on a clean runner and red every CI run. (r5, r6)
- Base/head for the classifier: `pull_request` → `github.event.pull_request.base.sha..head.sha`; `push` → `github.event.before..github.sha`. The output line is appended to `$GITHUB_OUTPUT` verbatim.

- [x] **Step 1: Write the failing test**

```python
# tools/test_ci_bookkeeping_filter.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest
from ci_bookkeeping_diff import classify

def test_status_only_is_bookkeeping():
    assert classify([".harness/roadmap_status.md"]) is True

def test_gate_rows_only_is_bookkeeping():
    assert classify([".harness/merge-gate-log.jsonl", ".harness/merge-gate-log.md"]) is True

def test_any_other_file_is_not():
    assert classify([".harness/roadmap_status.md", "harness-cp/src/x.py"]) is False

def test_empty_diff_raises():
    with pytest.raises(ValueError):
        classify([])
```

- [x] **Step 2: Run to verify it fails** — `uv run pytest tools/test_ci_bookkeeping_filter.py -v`; expected: import error.
- [x] **Step 3: Write the classifier** to the interface.
- [x] **Step 4: Run the test** — expected: 4 passed.
- [x] **Step 5: Add the `changes` and `gate-log-consistency` jobs and gate the heavy jobs** per the constraints.
- [x] **Step 6: Three witnesses before and after merging the workflow change.** Positive: the Task 1 PR touches `.github/` and `tools/`, so every job must run (`gh pr checks <n>` shows `changes` logging `bookkeeping=false` and pytest running). Negative: on a throwaway branch, make `tools/ci_bookkeeping_diff.py` exit 2 unconditionally and push; pytest must still run (proves the `always()` guard). After merge, the door's next refresh PR is the third witness: `gh pr checks <refresh-pr>` must show pytest, coverage, axis-isolation, typecheck, tools-coverage as `skipped`, `gate-log-consistency` as passed, and the PR mergeable. If any required check shows "Expected" instead of `skipped`, `git revert` and record the finding here; do not widen the filter.
- [x] **Step 7: Commit** — `git commit -m "ci: bookkeeping fast path — skip heavy jobs when only roadmap_status or gate-log files change"`.

**Landed** as PR #1503 → `b897542dc`, refresh #1504 → `9fb7ea033` (2026-09-03). Step 6 witnesses: positive, run 33774577684 (`changes` 13 s, `bookkeeping=false`, pytest ran); negative, run 33775581502 — the classifier STEP was forced to exit 2, not the classifier itself, because the self-guard makes a classifier edit unreachable on the same PR (`bookkeeping=false` before the classifier runs), and pytest still ran; third, refresh PR #1504's five heavy jobs `skipped` (run 33780380581, 55 s, measured in §0). Two deviations from the constraints as written: the classifier diffs `BASE...HEAD` (three-dot, the merge-base form a `pull_request` event needs) with `--no-renames`, so a renamed bookkeeping file is classified by both of its names. Step 8 stays decision-gated with Task 6 Step 6.

**Expected saving:** two runs per unit drop from ~455 s to ~60 s: the refresh PR run and the refresh-merge `main` push run (`github.event.before..github.sha` is the refresh commit alone). That is about 13 minutes of wall clock per landed unit, all of it inside the lease, so the door's hold shrinks from about 23 minutes to about 10. The "final head after gate rows" PR run stays full, because a `pull_request` diff is `base..head` and covers the whole PR.

- [ ] **Step 8 (optional, decision-gated): make the gate-rows head run cheap too.** Diffing `github.event.before..github.event.after` on `synchronize` would classify the gate-rows push as bookkeeping and skip pytest on that head. That reinterprets the rule at `.claude/skills/merge-gate/SKILL.md:229-237` ("wait for CI at that final head"): the evidence would come from the previous head plus `merge-gate-landing-delta` proving the delta is only the two log files. It is coherent, but it changes what the rule means, so it goes into the same AskUserQuestion as Task 6 Step 6 with the merge-gate skill edit attached, and is not built before that answer.

---

### Task 2: Prompt hook and banner signal (hooks category)

**Files:** modify `tools/hooks/lib.sh:267-286` (`hook_roadmap_next`) and `tools/hooks/loop_lib.sh:661` (`loop_notify_summary`, the reducer that renders `NOTIFY` rows into the banner; the emitter at `tools/merge_door.py:1254` writes one row per landing and is correct — the repeats are rows from successive landings rendered verbatim); tests `tools/hooks/test_lib_roadmap_next.sh` and `tools/hooks/test_loop_lib_notify.sh` (bash, same shape as `tools/hooks/test_permission_guard.sh`).

**Diagnosis (done 2026-09-03, re-run before editing).** `bash -c 'source tools/hooks/lib.sh; hook_roadmap_next .harness/roadmap_status.md'` prints nothing. The live "Current next action (post-#1497)" paragraph names its units without backticks ("The next implementable unit is **U-HE-37** …, then U-HE-38") and both existing extraction rules (`tools/hooks/lib.sh:272-276`, `:281-285`) require a backticked token.

**Design constraints:**
- Precedence in `hook_roadmap_next`: (0) a backticked `.harness/plan/<name>.md` pointer → `plan:<name>`; (1) the first bold `**U-…**` / `**R-…**` token — the pointer prose marks the next unit in bold; (2) the unit after the FIRST `then ` (quoted or not) — a last-`then` rule returns the successor's successor on the live prose ("…then U-HE-37 opens, then U-HE-38" names U-HE-37); (3) the existing backticked rules unchanged. (r3)
- Test fixtures mirror the live shapes; there is no assertion against the live `roadmap_status.md` (it goes stale with every refresh). The live witness is manual. (r3)
- `loop_notify_summary` promises the NEWEST five (`tail -5`, `loop_lib.sh:674`); dedupe must preserve last-occurrence order, before the cap — an awk two-pass (walk backwards keeping the first sighting, print forwards; no `tac`, macOS lacks it) — never `sort -u`, which replaces chronology with lexicographic order and can hide a newer notice. (r2, r4)

- [ ] **Step 1: Write the failing tests**

```bash
#!/usr/bin/env bash
# tools/hooks/test_lib_roadmap_next.sh
set -euo pipefail
source "$(dirname "$0")/lib.sh"
tmp=$(mktemp)
cat > "$tmp" <<'EOF'
## Next action
**Current next action (post-#1497).** U-HE-36 landed as the R3 eval arc. The next implementable unit is **U-HE-37** (S6 pilot gate), then U-HE-38.
EOF
[ "$(hook_roadmap_next "$tmp")" = "U-HE-37" ] || { echo "FAIL: live shape — bold next unit must win over the then-tail"; exit 1; }
cat > "$tmp" <<'EOF'
## Next action
**Current next action (post-#1497).** U-HE-36 landed as the R3 eval arc; the door owes its refresh, then U-HE-37 opens, then U-HE-38.
EOF
[ "$(hook_roadmap_next "$tmp")" = "U-HE-37" ] || { echo "FAIL: unquoted then-tail — the FIRST then, not the last"; exit 1; }
cat > "$tmp" <<'EOF'
## Next action
**Current next action.** Drive `.harness/plan/loop-optimization-plan-2026-09-03.md` Task 1, then U-HE-37.
EOF
[ "$(hook_roadmap_next "$tmp")" = "plan:loop-optimization-plan-2026-09-03" ] || { echo "FAIL: plan pointer"; exit 1; }
cat > "$tmp" <<'EOF'
## Next action
**Current next action.** Land `U-HE-40` next.
EOF
[ "$(hook_roadmap_next "$tmp")" = "U-HE-40" ] || { echo "FAIL: quoted unit still works"; exit 1; }
echo "ok"
```

`tools/hooks/test_loop_lib_notify.sh` (same shape) drives `loop_notify_summary` over a fixture ledger at a temp `loop_status_path()`: the same `NOTIFY` detail on three rows renders once; seven distinct details render the newest five in ledger order; a detail repeated at rows 1 and 8 of nine renders once, at row 8's position.

- [ ] **Step 2: Run them to verify they fail** — expected: `FAIL: live shape …`, and the notify suite failing on the repeat case.
- [ ] **Step 3: Extend the parser and the reducer** per the constraints.
- [ ] **Step 4: Run the tests** — expected: `ok` twice. Witness on the live file: `bash -c 'source tools/hooks/lib.sh; hook_roadmap_next .harness/roadmap_status.md'` prints the unit the pointer paragraph names as next (the plan pointer once Task 9's refresh installs it; `U-HE-37` for the post-#1497 prose), and a fresh prompt shows the same in `[roadmap] next=`; a new session with a `.codex-worktrees/` lane present shows its notice once.
- [ ] **Step 5: Commit** — `git add tools/hooks/lib.sh tools/hooks/loop_lib.sh tools/hooks/test_lib_roadmap_next.sh tools/hooks/test_loop_lib_notify.sh` and `git commit -m "fix(hooks): prompt-context next= recognizes plan pointers and bold units; notify reducer dedupes in order"`.

---

### Task 3: One-invocation arc close-out (serial tail)

The close-out after the door releases is eight serial steps (`.claude/skills/ship-pr/SKILL.md:387-644`). Reflect and `/context-save-lean` need the session; the exit report, metrics queue, and deferral rows do not. Fold those into one recipe.

**Files:** modify `justfile` (add `arc-close` next to `arc-exit-report` at line 265); modify `tools/hooks/permission-guard.sh` and `tools/hooks/test_permission_guard.sh` (the loop-mode allowlist entry); modify both ship-pr carriers (the §Arc exit report and §Arc-metrics capture sections of `.claude/skills/ship-pr/SKILL.md`, and the matching sections of `.agents/skills/ship-pr/SKILL.md`) to invoke `just arc-close`; test `tools/test_arc_close_recipe.py` (wired into `tools/codex-parity-check.sh`) plus a carrier-parity case in the shape of `tools/test_codex_workflow_parity.py`. Modify `.github/workflows/ci.yml` too: the recipe test EXECUTES `just`, and the runner has no `just` — install it (SHA-pinned `extractions/setup-just`) in the `test` job that runs the parity check.

**Interface.** `just arc-close <pr> <merge_sha> <checkpoint> [<arc-metrics queue arguments…>]` runs `just arc-exit-report --pr <pr> --merge-sha <merge_sha> --checkpoint <checkpoint>` then `just arc-metrics queue --pr <pr> <arguments…>`; each line in its own shell; `just` stops at the first non-zero exit.

**Design constraints:**
- Everything after the three exit-report positionals is forwarded verbatim to `arc-metrics queue`, whose contract is unchanged: `--transcript` is omitted when no transcript matches unambiguously, `--levers` is zero or many separate tokens (`ship-pr/SKILL.md:587-602`; `tools/arc_metrics.py` declares `--levers` with `nargs="*"`). Fixed positionals cannot express a valid close-out. (r1)
- The justfile sets `positional-arguments` and no `shell`, so recipe lines run under `sh -cu`: POSIX only — `shift 3` then `"$@"`, never `${@:4}`. (r2)
- The test EXECUTES the recipe: a shim `just` ahead of the real binary on `PATH` records the inner calls' argv (the real binary is resolved with `shutil.which` before the shim is prepended), so positional handling and glob preservation are exercised, not printed — `just -n` does not expand `$@`. (r2)
- Both ship-pr carriers change together with a parity witness; the cross-arc metrics drain stays as it is (its reason is durability, `ship-pr/SKILL.md:604-611`, `justfile:232-234`). (r5)
- The shim records each argv element separately (one NUL- or newline-delimited element per line, or JSON), never `"$*"`: a recipe that forwarded the whole tail as ONE argument via `"$*"` would produce the same flattened log as correct `"$@"` forwarding and the test would stay green while `arc_metrics` argparse failed. The assertions compare argument ARRAYS. (r6)
- The forwarded tail is checked before either inner call runs: a `--pr` (or `--pr=`) in it is refused, because `--pr` is bound to the first positional and argparse's last-wins would otherwise write the exit report for one PR and queue metrics for another. (codex r1 on b-230-task-3)
- `just arc-close` is added to the permission guard's loop-mode allowlist with `test_permission_guard.sh` cases; without it the new carrier command falls through to an approval prompt and is denied unattended. Task 3's file list includes `tools/hooks/permission-guard.sh` and its tests. (r6) **Grounded at the Task 3 arc:** the cited `just arc-exit-report` / `just arc-metrics` entries do not exist (`rg 'arc-exit-report|arc-metrics' tools/hooks/permission-guard.sh` is empty), so there was no exact-shape style to follow; `arc-close` rides the generic `just` verb alternation like every other allowlisted recipe — its variadic `*QUEUE_ARGS` swallows every trailing token, so no token can chain a second recipe, and the `_JUST_PLAIN_LINE` token grammar plus `_bash_args_safe` bound the arguments. Two forms stay at ask by those pre-existing walls and are pinned as ask cases: a glob `--round-logs '…/*.log'` (`*` is outside the token charset; widening is B-217's, not this task's — pass the round-log paths explicitly, `--round-logs` is `nargs="+"`) and a `--transcript` under `~` or anywhere outside the worktree (omit it in a loop-mode lane).

- [x] **Step 1: Write the failing test**

```python
# tools/test_arc_close_recipe.py
import json, os, shutil, subprocess

def _run(tmp_path, *args):
    shim = tmp_path / "bin"; shim.mkdir()
    log = tmp_path / "calls.txt"
    # one JSON array per inner call: argv ELEMENTS, so "$*" flattening cannot pass as "$@" forwarding
    (shim / "just").write_text("#!/usr/bin/env python3\nimport json, sys\nopen(" + repr(str(log)) + ", 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n")
    (shim / "just").chmod(0o755)
    real = shutil.which("just")
    env = {**os.environ, "PATH": f"{shim}{os.pathsep}{os.environ['PATH']}"}
    p = subprocess.run([real, "arc-close", *args], capture_output=True, text=True, env=env)
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return p.returncode, calls

def test_forwards_full_queue_tail(tmp_path):
    rc, calls = _run(tmp_path, "12", "abc123", "cp.md", "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
                     "--round-logs", "logs/*.log", "--transcript", "t.jsonl", "--levers", "B-1", "B-2")
    assert rc == 0
    assert calls == [
        ["arc-exit-report", "--pr", "12", "--merge-sha", "abc123", "--checkpoint", "cp.md"],
        ["arc-metrics", "queue", "--pr", "12", "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
         "--round-logs", "logs/*.log", "--transcript", "t.jsonl", "--levers", "B-1", "B-2"],
    ]

def test_omitting_transcript_and_levers_is_representable(tmp_path):
    rc, calls = _run(tmp_path, "12", "abc123", "cp.md", "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0", "--round-logs", "logs/*.log")
    assert rc == 0
    assert calls[1] == ["arc-metrics", "queue", "--pr", "12", "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0", "--round-logs", "logs/*.log"]
```

- [x] **Step 2: Run to verify it fails** — unknown recipe.
- [x] **Step 3: Add the recipe** per the interface and constraints.
- [x] **Step 4: Run the test** — expected: 2 passed.
- [x] **Step 5: Update both ship-pr carriers** — replace the two command blocks in §"Arc exit report" and §"Arc-metrics capture" with the single `just arc-close …` invocation; keep the surrounding rules (skip when the PR was itself the refresh; queue writes outside the repo; the transcript and lever rules verbatim). Add the parity case. Run `just codex-check`.
- [x] **Step 6: Commit** — `git commit -m "feat(just): arc-close folds exit-report + metrics queue into one close-out call"`. Landed at PR #1505 (`a8df62d59`), refresh #1506 (`a9173dc8d`).

---

### Task 4: Batched branch hygiene (one approval instead of N)

**Files:** create `tools/branch_hygiene_batch.py`; modify `justfile` (add `branch-hygiene-pending` and `branch-hygiene-resolve`); modify both ship-pr carriers at the branch-hygiene loop-mode paragraph (`.claude/skills/ship-pr/SKILL.md:471-480` and its `.agents` twin); test `tools/test_branch_hygiene_batch.py` (wired into `tools/codex-parity-check.sh`) plus the carrier-parity case.

**Interface.**
- `parse_pending(text) -> list[Deferral]` where `Deferral(item_id: str, branches: list[tuple[branch, pr]])`, read from the pending-HIL reducer's lines `[<lane>] <item-id> — branch hygiene close-out pending: <branch> (PR #N, merged <sha>, main run green)[ and <branch> (PR #M, …)]`; raises `UnreadableRow` for a pending row it cannot read.
- `verify_all(deferrals) -> dict[branch, head_oid]`; raises `VerificationMismatch` on the first branch whose PR is not `MERGED` or whose head branch differs.
- `build_push_command(branches: list[tuple[branch, oid]]) -> str` = `git push --atomic --force-with-lease=refs/heads/A:<oidA> … origin :refs/heads/A …`; raises `ValueError` on an empty list.
- `remote_absent(branch) -> bool` (ls-remote exit 2 only); `loop_resolve(item_id, note)`; `resolve_cleared(deferrals) -> list[Deferral]` (the ones still pending).
- CLI: `--pending PATH|-` (stdin), `--emit-command` (phase 1: print the push), `--resolve` (phase 2). Exit 2 unreadable row; 1 verification mismatch / items still present / nothing verified; 0 otherwise.
- Recipes: `branch-hygiene-pending` pipes `bash -c 'source tools/hooks/loop_lib.sh; loop_pending_hil_list'` into `--pending - --emit-command`; `branch-hygiene-resolve` pipes the same into `--pending - --resolve`.

**Design constraints:**
- Producer and parser share ONE row shape. The canonical defer text in both ship-pr carriers becomes `bash tools/04-loop/defer.sh <arc-id> "branch hygiene close-out pending: <branch> (PR #<N>, merged <merge-sha>, main run green) and roadmap-refresh-post-<N> (PR #<refresh-N>, merged <refresh-merge-sha>, main run green)"`; `parse_pending` is the authority on the shape. A pending row without a `<branch> (PR #N, merged` pair is refused loudly (`unreadable pending row: <row>` on stderr, exit 2), never skipped. (r1)
- Input is the pending-HIL reducer (`loop_pending_hil_list`, `tools/hooks/loop_lib.sh:392`; last-write-wins, so a `RESOLVED-HIL` row clears its item) over the canonical `loop_status_path()` (`loop_lib.sh:31`) — never the raw ledger or a hard-coded path. (r2)
- One verification failure aborts the whole batch (`verification mismatch: <branch> PR #N: <reason>`, exit 1, no command printed): a partially stale queue must never become a partially executed destructive push. (r2)
- The batch must resolve its own pending rows: the reducer is last-write-wins on the item id, so a deletion without its `RESOLVED-HIL` row is re-presented forever. `Deferral` keeps the item id for that. (r3)
- Two phases, each rerunnable. Phase 2 (`--resolve`) is keyed on the remote's state — every branch of the item absent (`git ls-remote --exit-code --heads origin refs/heads/<b>` exit 2, the one "genuinely absent" signal ship-pr already uses; any other non-zero aborts) — and only then appends the row through `loop_resolve` (`loop_lib.sh:286`). After a partial failure, rerunning resolves what is gone and reports `still present: <item> <branches>` for the rest without re-issuing a force-with-lease against OIDs that no longer exist. (r4)
- Ledger tokens are data, not program text: item ids are validated against `[A-Za-z0-9._-]+` at parse time (a row whose id fails is `UnreadableRow`), the resolve runs in-process through `subprocess` with `shlex.quote` on every argument, and no generated shell block is pasted. (r4, P1)
- The push is `--atomic`: one rejected `--force-with-lease` must not leave earlier refs deleted with the rest intact. (r5)
- Branch names are git refs and may legally contain `;`, `&`, `$()` and other shell metacharacters; the printed push is pasted by the operator, so `build_push_command` passes EVERY generated argument (branch, OID, ref spec) through `shlex.quote`, and a test feeds a hostile branch name (`feat/a;touch pwned`) and asserts the output contains no unquoted metacharacter. Item-id validation alone does not cover this. (r6, P1)
- The push itself is still typed by the operator in an interactive session — the permission guard denies force pushes to the loop by design; this tool collapses N approvals into one.
- **Grounded at the Task 4 arc — phase 1 probes origin too.** The first live batch showed 8 of 16 branches already absent on origin: `gh pr view` still reports a `headRefOid` for a merged PR whose branch was deleted, and a `--force-with-lease=<ref>:<oid>` on an absent ref is rejected as stale — under `--atomic` that rejects the WHOLE push. So `--emit-command` runs `remote_absent` over the verified branches (`partition_present`), names each absent one on stderr (`already absent on origin (branch-hygiene-resolve clears it): <branch>`), and leases only the present ones; every branch absent → `nothing to push`, exit 1, nothing on stdout. Phase 2 is unchanged and clears those items. Witnessed by execution, not read from the plan.
- **Grounded at the Task 4 arc — the reducer lists EVERY pending gate.** A row without the `branch hygiene close-out pending: ` marker is another tool's deferral (a credentials gate, say): it is typed `ForeignRow`, reported on stderr as `left pending (not a branch-hygiene deferral)`, and never refused — refusing it (a literal reading of r1) would fence every other gate behind branch hygiene; dropping it silently would be the skip r1 forbids. A row WITH the marker but without a `<branch> (PR #N, merged` pair is `UnreadableRow`, exit 2, as r1 says.
- **Grounded at the Task 4 arc — the plan's hostile-name test was wrong as written.** Its first assertion compared `argv[3]` without the `:<oid>` suffix the interface appends; its second stripped only the quoted lease argument while the quoted refspec still carried `;touch` — both failed against a correct implementation. The landed test asserts the exact six-element `shlex.split` argv and the `shlex.join` round-trip, which is the property both assertions were reaching for. The Step 1 block below is left as the plan wrote it.
- **Grounded at the Task 4 arc — no guard change.** `arc-close` (Task 3) needed a loop-mode allowlist entry because it runs INSIDE an unattended lane; these two recipes run only in the operator's interactive session (the carrier text says so), and a loop-mode lane still records the deferral through `defer.sh`. Both `gh pr view` and `git ls-remote` were already allowlisted read-only probes.
- **Grounded at the Task 4 arc — `loop_resolve` takes the ledger tokens as argv.** The item and note reach bash as `$1 $2` through `bash -c '… loop_resolve "$1" "$2"' <argv0> <item> <note>` — no interpolation into program text at all, which is strictly stronger than `shlex.quote`-then-interpolate; the hermetic end-to-end test lands a note carrying `$(touch pwned);` verbatim and checks nothing ran.

- [x] **Step 1: Write the failing test**

```python
# tools/test_branch_hygiene_batch.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest
import branch_hygiene_batch as m
from branch_hygiene_batch import Deferral, UnreadableRow, build_push_command, parse_pending, resolve_cleared

def test_two_branches_one_atomic_command():
    cmd = build_push_command([("feat/a", "aaa111"), ("roadmap-refresh-post-1", "bbb222")])
    assert cmd == ("git push --atomic --force-with-lease=refs/heads/feat/a:aaa111 "
                   "--force-with-lease=refs/heads/roadmap-refresh-post-1:bbb222 "
                   "origin :refs/heads/feat/a :refs/heads/roadmap-refresh-post-1")

def test_hostile_branch_name_is_quoted():
    import shlex
    cmd = build_push_command([("feat/a;touch pwned", "aaa111")])
    assert shlex.split(cmd)[3] == "--force-with-lease=refs/heads/feat/a;touch pwned"   # one argv element, not two
    assert ";touch" not in cmd.replace(shlex.quote("--force-with-lease=refs/heads/feat/a;touch pwned:aaa111"), "")

def test_empty_list_is_an_error():
    with pytest.raises(ValueError):
        build_push_command([])

def test_parse_pending_row_finds_both_branches_and_the_item():
    row = ("[lane-1] u-sr-08 — branch hygiene close-out pending: feat/u-sr-08-context-noise-deletions "
           "(PR #1489, merged 9032fead4, main run green) and roadmap-refresh-post-1489 "
           "(PR #1490, merged ff62189d2, main run green) — run the guarded force-with-lease delete block")
    assert parse_pending(row) == [Deferral("u-sr-08", [("feat/u-sr-08-context-noise-deletions", "1489"), ("roadmap-refresh-post-1489", "1490")])]

def test_bare_branch_row_is_refused_not_skipped():
    with pytest.raises(UnreadableRow):
        parse_pending("[lane-1] u-x — branch hygiene close-out pending: feat/u-x — run the guarded block")

def test_crafted_item_id_is_refused():
    with pytest.raises(UnreadableRow):
        parse_pending("[lane-1] $(touch pwned) — branch hygiene close-out pending: feat/a (PR #1, merged 111, main run green)")

def test_one_mismatch_aborts_the_batch(monkeypatch):
    monkeypatch.setattr(m, "pr_view", lambda pr: {"state": "MERGED", "headRefName": "feat/a" if pr == "1" else "other", "headRefOid": "aaa"})
    with pytest.raises(m.VerificationMismatch):
        m.verify_all([Deferral("u-a", [("feat/a", "1")]), Deferral("u-b", [("feat/b", "2")])])

def test_resolve_only_items_whose_branches_are_all_gone(monkeypatch):
    gone = {"feat/a": True, "roadmap-refresh-post-1": True, "feat/b": False}
    monkeypatch.setattr(m, "remote_absent", lambda branch: gone[branch])
    resolved = []
    monkeypatch.setattr(m, "loop_resolve", lambda item, note: resolved.append((item, note)))
    left = resolve_cleared([Deferral("u-a", [("feat/a", "1"), ("roadmap-refresh-post-1", "2")]), Deferral("u-b", [("feat/b", "3")])])
    assert [i for i, _ in resolved] == ["u-a"]
    assert left == [Deferral("u-b", [("feat/b", "3")])]
```

- [x] **Step 2: Run to verify it fails** — import error.
- [x] **Step 3: Write the tool** to the interface and constraints.
- [x] **Step 4: Run the test** — expected: 7 passed. Landed: the plan's 8 cases (the hostile-name test corrected, above) plus the live-shape, foreign-row, ls-remote-exit, hermetic end-to-end resolve, CLI exit-code, carrier-parity and recipe-shape cases — 28 passed.
- [x] **Step 5: Recipes and both carriers.** Add the two recipes; in both ship-pr carriers replace the canonical defer text with the one shape above and add: "In the next interactive session run `just branch-hygiene-pending`, paste the printed push (one approval clears every verified row), then run `just branch-hygiene-resolve` — it appends the `RESOLVED-HIL` row for each item whose branches are gone on origin, which is what makes the reducer stop presenting them; it is safe to rerun." Add the parity case.
- [x] **Step 6: Witness and commit.** As planned: `just branch-hygiene-pending` against the current three deferrals: six `branch oid` lines and one atomic push; `just branch-hygiene-resolve` run BEFORE the push reports all three items `still present` and resolves nothing. **As witnessed (2026-09-03):** the reducer presented 8 items / 16 branches; the first `--resolve` run resolved the 4 items whose 8 branches were already gone on origin (the ledger grew by exactly 4 `RESOLVED-HIL` rows, 1228091 → 1229035 bytes); after the phase-1 fix above, `just branch-hygiene-pending` prints eight `branch oid` lines and ONE atomic push for the 4 remaining items, and a second `--resolve` before the push reports all 4 `still present`, exit 1, no row appended. Do not run the push inside this task's PR; the operator runs it, then the resolve recipe, and the witness that the deferrals stop re-surfacing is the next session's banner. `git commit -m "feat(tools): branch_hygiene_batch — one guarded push for all deferred deletions"`.

---

### Task 5: Merge-gate emit in one call (smaller items)

Today the gate publishes three bindings, then emits three verdicts, each as its own `just` call (`merge-gate/SKILL.md:74-87,171-195`). `merge-gate-emit` exits 1 for a *recorded* BLOCK and 2 for a verdict NOT recorded (`justfile:354-355`).

**Files:** modify `tools/merge_gate_log.py` (an `emit-all` subcommand), `justfile` (a `merge-gate-emit-all *ARGS` forwarder next to `merge-gate-emit` at line 359), `tools/hooks/permission-guard.sh` and `tools/hooks/test_permission_guard.sh` (the loop-mode allowlist), `.claude/skills/merge-gate/SKILL.md:171-195`; test `tools/test_merge_gate_emit_all.py` (wired into `tools/codex-parity-check.sh`).

**Interface.** `merge_gate_log.py emit-all --pr <N> --arc-id <arc-id> --concurrency-json <f> --spec-json <f> --witness-json <f> [emit flags]` runs the existing `emit` path for `merge-gate-concurrency`, `merge-gate-spec-conformance`, `merge-gate-witness-adequacy` in that order and exits with the worst outcome across all three lenses (2 not recorded > 1 recorded BLOCK > 0).

**Design constraints:**
- A recorded BLOCK is a result, not an abort: the loop lives in Python and all three lenses are always emitted (a multi-line just recipe would stop at the first exit 1 and leave later lenses unrecorded, breaching the all-three-verdicts audit contract). (r1)
- Resumable per lens ONLY if the complete binding is persisted. The JSONL envelope (`Spec_HE_Loop_Lanes_v1.md:632`) persists `arc_id`, `head_sha`, `base_sha`, `diff_digest`, `producer` but NOT the lens `prompt_version` or the carrier `config_hash` that `lens_binding` also binds gate validity to, so a row cannot tell a verdict produced before a lens-prompt or carrier change from a current one. Two admissible designs, the arc picks one and states it: (a) `emit-all` writes its own resume record (out-of-repo or under `.harness/tmp/`) carrying the full six-field binding per emitted lens, and resumes only against that record; (b) no resumption — a re-run re-emits all three lenses. Skipping on the JSONL row alone is foreclosed. (r3, r4, r5, r6)
- A skipped lens's RECORDED outcome contributes to the exit code: a resume that skips a recorded BLOCK and records an APPROVE for the missing lens exits 1, never 0 — a split verdict must never read as all-approve. (r5, P1)
- `just merge-gate-emit-all` is added to the permission guard's loop-mode allowlist in the same exact-shape style as the existing `merge-gate-emit` entry, with `test_permission_guard.sh` cases (allowed in loop mode; the raw denied verbs unchanged); without it the recipe falls through to ask and is denied unattended. (r5)
- One skill carrier (`.claude/skills/merge-gate/SKILL.md`; `.agents/skills/merge-gate/` holds no `SKILL.md`).

- [ ] **Step 1: Write the failing test** — monkeypatch the single-emit function and record calls: (a) concurrency returns 1, the others 0 → all three emitted in order, exit 1; (b) the middle lens returns 2 → the third is still emitted, exit 2; (c) resume: a temp JSONL already holds rows for the first two lenses matching the full current binding (real row shape, no `pr`), the first a recorded BLOCK → only `merge-gate-witness-adequacy` is emitted, the log gains exactly one row, exit 1 even though the emitted lens returned 0; (d) a row for the first lens at the same head but a different `base_sha` is NOT a match → that lens is re-emitted; (e) `just --show merge-gate-emit-all` names the subcommand.
- [ ] **Step 2: Run it, expect FAIL.**
- [ ] **Step 3: Add the subcommand, the recipe, and the guard allowlist entry + tests.**
- [ ] **Step 4: Run the tests, expect PASS** (including `bash tools/hooks/test_permission_guard.sh`).
- [ ] **Step 5: Wire the test into `tools/codex-parity-check.sh`, update the skill text, commit** — `git commit -m "feat(just): merge-gate-emit-all"`.

The second disjointness check at ship time stays: HEAD changed since selection, so it is not a duplicate.

---

### Task 6: Concurrency lens on demand (duplicate reviews, spec-gated)

Basis: the concurrency lens has 1 raw / 0 net-of-rejected unique catches in 88 findings; witness-adequacy has 22 raw / 19 and spec-conformance 10 (§0; the accepted-only figure comes from Task 0). Running the concurrency lens only when the diff touches a shared-state, process-isolation or timeout/cancellation surface removes one subagent from the gate rounds the detector clears; Step 5 measures how many that is. Running fewer lenses is what C-HE-34 forecloses — "No collapsing of review layers to cut the 68%" (`Spec_HE_Loop_Lanes_v1.md:823`) — so an operator answer cannot enable it directly: Steps 1–5 build the detector and the measurement (mode-agnostic), Step 6 asks once, and a *yes* opens a spec leg (change note qualifying C-HE-34 for a detector-gated lens, clearance marker, HE plan update, landed as a doc-only PR) before the code and skill edits land.

**Files:** create `tools/concurrency_surface.py`; test `tools/test_concurrency_surface.py` (wired into `tools/codex-parity-check.sh`). Only after the spec leg is cleared: `tools/merge_gate_log.py` (the typed skip path), `tools/hooks/permission-guard.sh` + tests, `.claude/skills/merge-gate/SKILL.md:110-169` and `:197-219`.

**Interface.** `touches_concurrency(diff: str) -> bool` over unified-diff text (`git diff -U0 <base>..<head>`); raises `EmptyDiff` when the input has no `+`/`-` content lines. CLI reads stdin and prints `concurrency=true|false`; exit 2 with `run the lens` on `EmptyDiff`.

**Design constraints:**
- The detector reads the DIFF, not surviving files: added AND removed lines of every path, so a deleted file, a removed lock, and a shell or workflow change all count. (r1)
- Token allowlist: `asyncio.(gather|create_task|Lock|Semaphore|Queue|timeout|wait_for|shield)`, `CancelledError`, `.cancel(`, `TimeoutError`, `threading`, `multiprocessing`, `concurrent.futures`, `fcntl`, `flock`, `os.link`, `O_EXCL`, `subprocess.Popen`, `Lock(`, `Semaphore(`, `.exists()`, `.is_file()`, `os.path.exists`, `.unlink(`, `os.remove`, `os.rename`, `os.replace`, `global `, `nonlocal ` — every construct the lens prompt names (`.claude/skills/merge-gate/SKILL.md:110-169`, timeout/cancellation at `:129-130`) plus the path-TOCTOU and module-global shapes. Deliberately not `await ` or bare `asyncio`: nearly every harness diff is async. (r2, r3)
- The detector is an allowlist and therefore FAIL-OPEN by construction for a surface it does not name (a check-then-act spelled without these calls, a shared dict mutated through a method). That residual is the risk Step 5 measures and the Step 6 spec leg must state as its bound; no sentence in this plan or the code may claim the detector fails closed on unknown surfaces. (r3)
- Empty, header-only or binary-only input is UNKNOWN, never "no surface": `EmptyDiff` → exit 2 → the lens runs. The skill step skips the lens ONLY on a literal `concurrency=false`. (r4)
- The typed skip row (`no_finding`, `finding_type: lens_skipped`, `cause_attribution: detector_no_surface`) is written ONLY by an emit command that itself runs the detector on the bound diff (`diff_digest` from `lens_binding`) and records the detector's verdict in the row — never from caller-supplied reason text, which a headless agent could use to claim a skip and bypass the reviewer. That command gets its own exact-shape guard allowlist entry and `test_permission_guard.sh` cases; the existing `emit` parses only a bound reviewer verdict (`clean_approve` at `merge_gate_log.py:196`) and cannot carry a skip. (r3, r5 P1)

- [ ] **Step 1: Write the failing test**

```python
# tools/test_concurrency_surface.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest
from concurrency_surface import EmptyDiff, touches_concurrency

def test_added_lock_is_a_surface():
    assert touches_concurrency("+++ b/a.py\n+import asyncio\n+lock = asyncio.Lock()\n") is True

def test_removed_lock_is_a_surface():
    assert touches_concurrency("+++ b/a.py\n-lock = asyncio.Lock()\n+lock = None\n") is True

def test_deleted_fcntl_file_is_a_surface():
    assert touches_concurrency("--- a/c.py\n+++ /dev/null\n-import fcntl\n") is True

def test_shell_flock_is_a_surface():
    assert touches_concurrency("+++ b/tools/hooks/x.sh\n+flock -n 9 || exit 1\n") is True

def test_timeout_and_cancellation_are_surfaces():
    assert touches_concurrency("+++ b/e.py\n+async with asyncio.timeout(5):\n") is True
    assert touches_concurrency("+++ b/f.py\n-except asyncio.CancelledError:\n+except Exception:\n") is True

def test_path_toctou_and_module_global_are_surfaces():
    assert touches_concurrency("+++ b/g.py\n+if path.exists():\n+    path.unlink()\n") is True
    assert touches_concurrency("+++ b/h.py\n+    global _registry\n") is True

def test_plain_async_def_is_not_a_surface():
    assert touches_concurrency("+++ b/d.py\n+import asyncio\n+async def x(): await y()\n") is False

def test_plain_diff_is_not():
    assert touches_concurrency("+++ b/b.py\n+def y(): return 1\n") is False

def test_empty_or_contentless_input_fails_closed():
    for bad in ("", "\n", "+++ b/x.bin\n--- a/x.bin\n", "Binary files a/x and b/x differ\n"):
        with pytest.raises(EmptyDiff):
            touches_concurrency(bad)
```

- [ ] **Step 2: Run it, expect FAIL.**
- [ ] **Step 3: Write the detector** to the interface and constraints.
- [ ] **Step 4: Run the test, expect PASS. Wire the test into `tools/codex-parity-check.sh`; commit** `git commit -m "feat(tools): concurrency_surface detector (merge-gate lens gating, spec leg pending)"`.
- [ ] **Step 5: Measure on history** — for the last 20 gate rounds, run the detector on each PR's `git diff -U0 base..head` and record how many rounds would have skipped the lens and whether any of the lens's 88 findings fell in a skipped round; any ACCEPTED concurrency finding in a would-skip round is a measured instance of the fail-open bound, recorded by finding id. Put the table in this plan under §0.
- [ ] **Step 6: One AskUserQuestion** with the table and the fail-open bound stated: (a) open the C-HE-34 spec leg for a detector-gated concurrency lens with the typed skip path above, so C-HE-29 accounting stays whole; (b) keep three lenses always. On (a): spec + marker PR first (doc-only), then the code PR (typed skip path + guard entry + tests) and the skill edit. On (b): Steps 1–5 stay as a measurement instrument and this task closes.

The Codex re-run after a lens BLOCK stays. A fix is new code and the out-of-family reviewer has never seen it; the log shows 1765 wrapper-written Codex rows against 310 lens-written rows at the Task 0 head (`codex_rows` / `lens_rows`), so the re-run is where the catches are.

---

### Task 7: Spec leg — `--delete-branch` in the fixed merge string (optional, policy change)

Deleting the topic branch inside the door removes the deferral queue Task 4 batches. It conflicts with the standing rule that branch deletion is a per-instance human decision (`ship-pr/SKILL.md:471-480`). Offer it; do not build it unless the operator changes the rule.

The permission guard is not on the path: the door runs `gh pr merge` from a Python subprocess inside `tools/merge_door.py`, which the Bash PreToolUse guard never sees, so no allowlist carve-out is needed and the two guard tests that deny the raw verbs — `gh pr merge … --delete-branch` at `tools/hooks/test_permission_guard.sh:174` and `gh pr close … --delete-branch` at `:279` — stay exactly as they are. Allowing the raw merge would bypass the lease-enforcing wrapper; the close verb is unrelated destructive behaviour. Both remain denied under every outcome of this task. (r1, P1)

**Files (only after the decision):** `.harness/spec/Spec_HE_Loop_Lanes_v1.md:294` (C-HE-06 §4 iv) and `:334-338` (C-HE-07 §1), bumped to the next unallocated version at the time the leg opens, with a change note; `.harness/clearance/spec-he-loop-lanes-v<that version>-cleared-<date>.md`; `tools/merge_door.py:896` (the fixed string), `tools/hooks/safe-merge.sh:2-4` (its comment quoting the string), `.harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md`, `tools/test_merge_door.py` (the fixed-string witness). No permission-guard or guard-test change.

- [ ] **Step 1:** Present the decision in the same AskUserQuestion as Task 6 Step 6, recommending **no** for now: Task 4 already collapses the cost to one approval per session, and the rule exists because deletion is irreversible.
- [ ] **Step 2 (only on yes):** file the spec change note, land the spec + marker PR first (doc-only, no code, so the context guard's DESIGN_IMPL_MIX rule stays clean), then land the code PR with the file edits above.

---

### Task 8: Spec leg — lease scope and N-merge refresh (deferred, trigger-gated)

Releasing the lease after the content merge and letting one refresh cover N merges would end serialization, but it needs three coupled changes: C-HE-06 invariants (`Spec_HE_Loop_Lanes_v1.md:317-321`), the §12.2.1 one-commit fixed point in root `CLAUDE.md`, and `_owed_lag` in `tools/codex_context_guard.py:443-469`. The data cannot justify it yet, in either direction: the only `merge-door-lease-acquire` row the door writes is the budget-exhausted one (`tools/merge_door.py:1965`, `lease_acquire_budget_exhausted`, after twelve backoffs of up to ten minutes). A yield that resolves inside the budget writes nothing, so "2 rows in 76 arcs" counts hour-long stalls, not contention. Task 1 cuts the hold from about 23 minutes to about 10 regardless.

**Design constraints for Step 1:**
- The observation goes OUT of the repo. A row appended to the tracked `.harness/merge-gate-log.jsonl` while `wait_for_door` is running lands after the PR's final committed head and CI gate; when contention clears the door merges the committed head and the row is left as dirty, unmerged worktree state that blocks cleanup and never reaches durable history (the u-he-36 `refresh_pr_ci_not_green` row this registration PR had to carry is the same defect on the door's post-merge path). The yield therefore goes to the shared, append-only `loop_status.md` through the writer the door already uses for its `DEFERRED-HIL` rows — `_notify` (`tools/merge_door.py:986`) over `reservations.emit_loop_row` (`tools/reservations.py:750`). (r1)
- Exactly ONE row per contention event: emitted at the first `held` observation of a `wait_for_door` call (backoff index 0), never on the later retries — an every-retry emitter would inflate the trigger by up to eleven rows per event. Kind `NOTIFY`, cause exactly `merge-door-lease-acquire:lease_held_yield`, detail `holder=<holder arc id> backoff=0`. (r3)
- `wait_for_door` sleeps and retries in place (base 30 s ×2, cap 10 min, 12 attempts; `tools/merge_door.py:1710-1740`); it never hands control back to the caller. The diagram at `docs/diagrams/code-loop/04-merge-refresh.workflow.json` and the ship-pr sentence at `.claude/skills/ship-pr/SKILL.md:265-267` say so since this PR. (r2, r3)

- [ ] **Step 1: Make contention visible.** Emit the row per the constraints; touch nothing in acquire, release, the gate log, or the invariants at `Spec_HE_Loop_Lanes_v1.md:317-321`. Test: `tools/test_merge_door.py` gains one case driving `wait_for_door` through three `held` observations before success (patched `sleep`, patched `emit_loop_row` recording every call) and asserting exactly ONE row, kind `NOTIFY`, the exact cause, the holder's arc id and `backoff=0` in the detail, and the tracked gate log byte-identical before and after.
- [ ] **Step 2:** Register a forward-register row (the next free id; `B-231` went to the failover-marker residual from Task 0) titled "Merge-door lease released after content merge; refresh covers N merges", with the trigger "more than 5 `lease_held_yield` rows in any 30-day window after Task 1 lands" and the three cites above.
- [ ] **Step 3:** Extend `tools/loop_cost_baseline.py` with `--loop-status PATH` evaluating the Step 2 trigger as a ROLLING window — the maximum number of `lease_held_yield` NOTIFY rows whose timestamps fall in any 30-day span (reported as `lease_held_yields_30d_max` beside the lifetime `lease_held_yields`); a lifetime count would stay "triggered" forever after six events spread over years. Boundary tests: six rows 29 days apart end-to-end → 6; six rows spanning 31 days → 5; timestamps parsed from the ledger's ISO column. Re-run it at each roadmap refresh; when the trigger fires, open the spec leg as a Class 2 decision with a proposed text at the next unallocated version. (r6)

B-230 closes only after Steps 1–3 are all landed: an umbrella closed after Step 1 alone would strand the observations with no reachable trigger. (r4)

---

### Task 9: Register the plan so the loop can find it (do this first)

`roadmap-continue` derives the next action from `.harness/roadmap_status.md` and `.harness/forward-register.yaml` (root `CLAUDE.md` §12.4.1). An unregistered plan is parked.

**Files:** `.harness/forward-register.yaml` (append one umbrella row; bump `snapshot:` in the same commit, as every row addition does) and its prose twin `.harness/post-phase-8-forward-register.md`; `.harness/.next-action-draft` (gitignored; consumed by the door's next refresh).

- [x] **Step 1: Append the umbrella row** using the next free id after `B-229` (check with `grep -n '^- id: B-' .harness/forward-register.yaml | tail -1`):

```yaml
- id: B-230
  title: >-
    Loop optimization program: CI bookkeeping fast path, prompt-hook signal, one-call
    arc close-out, batched branch hygiene, merge-gate emit-all, lens gating decision,
    two trigger-gated spec legs
  pr: 'PR pending (b-230-register)'
  status: open
  summary: 'SURFACED by the Archify loop diagrams (docs/diagrams/code-loop/, 2026-09-03)
    and grounded the same day: five CI runs per landed unit with pytest at 450 s each,
    a merge-door lease held across two of them, 35 of 49 gate passes raised by a single
    lens (Task 0's head-bound count; the pre-registration read was 33 of 48), and a prompt hook printing next=? because the pointer prose stopped quoting
    unit ids. Plan with per-task witnesses at
    .harness/plan/loop-optimization-plan-2026-09-03.md.'
  close_out: 'OPEN — closes when Tasks 0-5 are merged with their witnesses recorded in
    the plan §0, Task 6 and Task 7 have an operator answer, and Task 8 Steps 1-3 are
    all landed: the yield row emitted, the trigger row registered, and the counter
    wired into the baseline script — an umbrella closed after Step 1 alone would strand
    the observations with no reachable trigger.'
  council: 'NO — workspace-ops tooling; the two spec legs (Tasks 7-8) are separately
    decision-gated inside the plan.'
  heading: '### B-230 · Loop optimization program *(surfaced by the Archify loop diagrams, 2026-09-03)*'
```

The field set above mirrors `B-229`. `status` must be one of the register enum values in `tools/forward_register.py` (`open`, not `active`), and `tools/forward_register.py --check` also requires a matching `### B-230 · …` block in `.harness/post-phase-8-forward-register.md` whose heading equals the `heading:` field byte-for-byte. `just check` runs its tally gate.

- [ ] **Step 2: Point the next action at the plan.** Write `.harness/.next-action-draft` with first line `post-pr: <N>` for the PR that lands this registration, then one paragraph: "Drive `.harness/plan/loop-optimization-plan-2026-09-03.md` Task 0 then Task 1 (B-230); then U-HE-37." The door's refresh installs it, and after Task 2 the prompt hook shows `next=plan:loop-optimization-plan-2026-09-03`.

- [ ] **Step 3: Land it** as a doc-only PR (`register`, `snapshot`, this plan file, the diagrams it cites); `just check` green; no merge-gate (no code surface); commit `ops: register B-230 loop optimization program`.

## Order and expected effect

| Order | Task | Kind | Saving per landed unit | Risk |
|---|---|---|---|---|
| 0 | Task 9 registration | bookkeeping | none; makes the plan reachable | none |
| 1 | Task 0 baseline | tooling | none; the witness for everything else | none |
| 2 | Task 1 CI fast path | workspace-ops | about 13 min wall clock (two runs); lease hold from ~23 to ~10 min | required checks must report `skipped`, verified on the first refresh PR |
| 3 | Task 2 hooks | workspace-ops | one useful line per prompt instead of `next=?`; 3 fewer banner lines | none |
| 4 | Task 3 arc-close | workspace-ops | 2 fewer serial steps and tool calls per arc | none |
| 5 | Task 4 branch batch | workspace-ops | N approvals become 1 per session | none; push stays manual |
| 6 | Task 5 emit-all | workspace-ops | 2 fewer tool calls per gate round | none |
| 7 | Task 6 lens gating | tooling (detector, Steps 1–5) + spec leg (C-HE-34, Step 6) | one subagent fewer in the gate rounds the detector clears (Step 5 measures how many) | collapses a review layer, which C-HE-34 forecloses; ask once with data, and a yes opens the spec leg before any skill edit |
| 8 | Task 7 delete-branch | spec leg, policy | removes the deferral queue | irreversible deletion moves into the door; recommend no |
| 9 | Task 8 lease scope | spec leg, trigger-gated | ends serialization | contention is unmeasured until Step 1 lands; two hour-long stalls on record |

Each task is its own PR and its own arc through the loop it optimizes. Re-run `uv run python tools/loop_cost_baseline.py` and `gh run view <latest main run> --json jobs` after each merge and append the numbers to §0.

## Review trail (b-230-register, the registration PR)

Five codex rounds against this plan while it still carried draft implementations; every finding accepted and carried above as a constraint marked with its round:

| Round | Head | Findings | What they were |
|---|---|---|---|
| r1 | `02f656c72` | 8 (1 P1) | clean rounds and rejected adjudications missing from the baseline; fixed positionals that could not express a valid close-out; parser and producer disagreeing on the deferral row shape; a just recipe stopping at a recorded BLOCK; a detector reading surviving files instead of the diff; lens gating and `--delete-branch` mis-classified as operator-only decisions (C-HE-34; the guard is not on the door's path); a mid-door gate-log write that could never reach merged history |
| r2 | `2a3c66b8b` | 8 | a movable `actions/checkout@v4` tag on the job that decides whether heavy checks run; dedupe at the emitter instead of the reducer; Bash-only `${@:4}` under `sh -cu` with a dry-run test that could not exercise it; a hard-coded ledger path bypassing `loop_status_path()` and the pending reducer; a batch dropping failed verifications instead of aborting; timeout/cancellation surfaces missing from the detector; pre-assigned spec versions that collide; the diagram and ship-pr saying a held lease *yields* when `wait_for_door` sleeps in place |
| r3 | `034b392ee` | 7 | a last-`then` rule returning U-HE-38 on the live prose; a batch that never appended the `RESOLVED-HIL` rows the last-write-wins reducer needs; a non-resumable emit-all; a fail-closed claim a token allowlist cannot make; a `lens skipped` row with no emitter; a contention test that let an every-retry emitter pass; the diagram's primary held node |
| r4 | `4ff4006ac` | 8 (1 P1) | a ledger item id interpolated unquoted into `bash -c`; a push-then-resolve block not rerunnable after a partial failure; `sort -u` reordering the newest-five cap; a resume key naming a `pr` field the JSONL row does not carry; an empty or binary diff read as "no surface"; bare sibling imports the importlib suite rejects; two tools tests left out of the parity list; an umbrella close_out that could close before its trigger existed |
| r6 | `66e451ed9` | 7 (1 P1) | on the rescoped plan: unquoted git ref names in the pasted push (refs may carry `;`/`&`/`$()`); the "stdlib-only" consistency job importing `jsonschema` through two siblings; `just arc-close` missing from the guard allowlist; a `"$*"` shim that could not tell flattened forwarding from `"$@"`; a resume key naming `prompt_version`/`config_hash` the JSONL envelope does not persist; a lifetime yield count that cannot evaluate a 30-day window; the diagram's main path bypassing the merge-SHA CI node |
| r5 | `3d5b1e127` | 8 (2 P1) | a resume that could skip a recorded BLOCK and exit 0; a skip row any caller could claim without running the detector; a resume key ignoring `base_sha`/`diff_digest`; `merge-gate-emit-all` missing from the guard allowlist; "net of rejected" where C-HE-29 requires a last disposition of `accepted`; the fast path skipping the only job that runs the gate-log consistency check; a non-atomic multi-ref push; the `.agents` ship-pr carrier left out |

After r5 the plan was rescoped to interfaces, tests and constraints; r6 ran on the rescoped text and still produced seven new design findings (absorbed above as constraints, the P1 with its test). Six rounds, 46 findings, 46 accepted, none rejected, no APPROVE: this is the "yield is not front-loaded when inventing" pattern, and the lean review protocol for doc PRs (operator directive 2026-08-11: codex capped at one round for doc/config PRs; close a non-convergent loop at the arms-race point with the residual class recorded) closes the loop here — no r7. **Residual class recorded:** the plan is a design; further findings against any task's design are expected and are absorbed in that task's own arc, which writes the code, runs its own codex rounds against it, and is the reviewer of record. The six rounds' constraints are the floor each arc starts from, not a claim that the designs are complete.

## Self-review

- Registration: Task 9 first, so the loop derives the next task instead of parking the plan.
- Coverage: CI runs → Task 1; serialization → Task 1 (duration) + Task 8 (trigger); duplicate reviews → Task 6 (spec-gated) with the Codex re-run kept; hooks → Task 2 (the two real defects); close-out tail and cross-arc coupling → Task 3 (tail) with the coupling left in place for a stated reason; smaller items → Tasks 4 and 5, disjointness check kept.
- No task edits the fixed merge string, releases the lease early, drops the CI-at-final-head rule, or runs fewer review lenses without a spec leg (C-HE-06, C-HE-07, C-HE-34); no task touches the permission guard's denial of the raw `gh pr merge` / `gh pr close --delete-branch` verbs.
- Names used across tasks: `classify`, `build_push_command`, `parse_pending`, `Deferral`, `UnreadableRow`, `verify_all`, `VerificationMismatch`, `remote_absent`, `loop_resolve`, `resolve_cleared`, `touches_concurrency`, `EmptyDiff` are each defined in the task that introduces them.
