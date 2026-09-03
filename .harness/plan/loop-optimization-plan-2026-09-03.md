# Code Implementation Loop Optimization Plan

> **For agentic workers:** each task is one arc through this workspace's loop: `roadmap-continue` picks it from the forward-register row Task 9 creates, the arc lands through `ship-pr` (Codex round, CI, merge-gate for code-touching diffs, door, refresh). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut the wall-clock and token cost of one landed unit (continue → refresh merge) without weakening any gate that has caught a real defect.

**Architecture:** Six cost categories were surfaced by the Archify diagrams at `docs/diagrams/code-loop/`. Grounding on 2026-09-03 sorted them into workspace-ops changes (CI workflow, hooks, just recipes, skill procedure) that land as ordinary PRs, and spec-governed changes (C-HE-06 / C-HE-07 in `.harness/spec/Spec_HE_Loop_Lanes_v1.md`, cleared v1.7 on 2026-09-02) that need a spec leg plus a clearance marker before any code moves. Tasks are ordered by measured value over cost. Every task carries the witness that proves its saving against the baseline in §0.

**Tech Stack:** GitHub Actions (`.github/workflows/ci.yml`), bash hooks under `tools/hooks/`, `justfile` recipes, Python 3.12 tools under `tools/`, the merge-gate and ship-pr skills under `.claude/skills/`.

## Global Constraints

- Posture is mode-agnostic for Tasks 0–5 and for Task 6 Steps 1–5 (they touch `.github/`, `tools/`, `justfile`, `.claude/skills/`). Task 6 Step 6 (running fewer lenses), Task 7 and Task 8 change what `.harness/spec/Spec_HE_Loop_Lanes_v1.md` guarantees — C-HE-34 ("No collapsing of review layers", `Spec_HE_Loop_Lanes_v1.md:823`), C-HE-06 §4 and C-HE-07 §1, C-HE-06 invariants — and need a version bump, a change note, a clearance marker under `.harness/clearance/`, and the HE plan update, before any skill or code change lands. An operator answer alone does not authorize them; it authorizes opening the spec leg.
- The fixed merge string `gh pr merge <pr> --squash --match-head-commit <head_sha>` (`Spec_HE_Loop_Lanes_v1.md:294`, `tools/merge_door.py:896`) may not change in any workspace-ops task.
- The lease is never released while the merge SHA's own `main` run or the terminating refresh is unconfirmed (`Spec_HE_Loop_Lanes_v1.md:321`). No workspace-ops task may release earlier.
- Gate rows are committed before merge and CI must be green at that final head (`.claude/skills/merge-gate/SKILL.md:229-237`). Task 1 makes that CI run cheap; it does not remove it.
- Branch deletion requires an explicit per-instance human approval, loop mode included (`.claude/skills/ship-pr/SKILL.md:471-480`; deny rule at `tools/hooks/permission-guard.sh:618`). Task 4 reduces the number of prompts, not the requirement.
- Every merged PR is a normal arc: Codex round, CI, merge-gate for code-touching diffs, door, refresh.
- All required status checks on `main` (12 contexts, `strict: true`) must keep reporting a conclusion on every PR. GitHub's docs state "A job that is skipped will report its status as 'Success'. It will not prevent a pull request from merging, even if it is a required check" (docs.github.com, Using conditions to control job execution); a job that never starts, as with a workflow-level `paths:` filter, leaves the check "Expected" and blocks the merge. Task 1 relies on job-level `if:` for exactly this reason and never uses workflow-level `paths:`.

---

## §0 Baseline (measured 2026-09-03, re-measure before and after each task)

| Measure | Value | How measured |
|---|---|---|
| CI wall clock, `main` push run 33729280509 | 455 s; pytest job 450 s, coverage 288 s, every other job ≤ 51 s | `gh run view <id> --json jobs` |
| Required checks on `main` | 12 blocking contexts, `strict: true` | `gh api repos/{owner}/{repo}/branches/main/protection` |
| CI runs per landed code unit | 5: PR head, PR final head after gate rows, main on merge SHA, refresh PR, main on refresh merge | ship-pr skill + `tools/merge_door.py:1286-1577` |
| CI path filtering today | none in `ci.yml:33-40`; only `x-al-3-guard.yml:6-8` filters | grounding |
| Lease-acquire budget-exhausted events | 2 rows in `.harness/merge-gate-log.jsonl` across 65 arcs; in-budget yields are not logged (`tools/merge_door.py:1965`) | script in Task 0 |
| Review rounds per arc | median 7, max 24; Codex wrapper wrote 2039 of 2455 log rows | script in Task 0 |
| Gate rounds with findings | 48; in 33 of them exactly one lens raised findings | script in Task 0 |
| Unique catches by lens | raw `unique_catch` flags: witness-adequacy 22, spec-conformance 10, concurrency 1 (of 88 concurrency findings). Net of `finding_adjudication` rows with `disposition: rejected` (the contract-valid figure, C-HE-24 §5): 19 / 10 / 0, measured by codex r1 on the b-230-register head `02f656c72` | script in Task 0 (reports both) |
| Per-call hook cost | `post-merge-refresh.sh:45`, `precmd-clear-cache.sh:28`, `rtk-shape-guard.sh:69` exit within one grep of an ordinary Bash call; `permission-guard.sh:67` exits unless loop mode | grounding |
| Prompt hook signal | `[roadmap] next=?` on every prompt this session (`prompt-context.sh:57` prints `?` when `hook_roadmap_next` returns empty, `tools/hooks/lib.sh:267-286`) | observed |
| Branch-hygiene deferrals waiting on the operator | 3 plus one TTL re-surface in the session banner | observed |

The hooks category collapses to two defects (the empty `next=` token and duplicated banner lines); the per-call hooks are already cheap. The serialization category collapses to lease *duration* until Task 8 Step 1 makes in-budget contention measurable; only two hour-long stalls are on record in 65 arcs.

---

### Task 0: Baseline script

The log has four `record_kind` values (`finding`, `no_finding`, `finding_adjudication`, `reviewer_unavailable`; count them with `rg -o '"record_kind": "[^"]*"' .harness/merge-gate-log.jsonl | sort | uniq -c`). A round exists whenever any of them carries a `round_n`, so a clean round (`no_finding`) and a clean-only arc count toward rounds-per-arc; and a `unique_catch` flag counts only while no `finding_adjudication` row rejects its `finding_id` (codex r1 on b-230-register: the finding-rows-only draft reported 22/10/1 where the contract-valid figure is 19/10/0). Door rows carry `round_n: null` and are not rounds.

**Files:**
- Create: `tools/loop_cost_baseline.py`
- Test: `tools/test_loop_cost_baseline.py`

**Interfaces:**
- Produces: `python tools/loop_cost_baseline.py [--log PATH]` printing a JSON object with keys `rows`, `arcs`, `rounds_per_arc_median`, `gate_rounds_with_findings`, `single_lens_rounds`, `unique_catch_by_producer` (net of rejected adjudications), `unique_catch_rejected`, `lease_acquire_events`.

- [ ] **Step 1: Write the failing test**

```python
# tools/test_loop_cost_baseline.py
import json, subprocess, sys

def test_baseline_reports_expected_keys(tmp_path):
    log = tmp_path / "log.jsonl"
    rows = [
        {"record_kind": "finding", "arc_id": "a", "round_n": 1, "producer": "codex_review_wrapper", "finding_id": "c1", "unique_catch": False},
        {"record_kind": "finding", "arc_id": "a", "round_n": 2, "producer": "merge-gate-witness-adequacy", "finding_id": "w1", "unique_catch": True},
        {"record_kind": "finding", "arc_id": "a", "round_n": 2, "producer": "merge-gate-spec-conformance", "finding_id": "s1", "unique_catch": True},
        {"record_kind": "finding_adjudication", "arc_id": "a", "round_n": 2, "finding_id": "s1", "disposition": "rejected"},
        {"record_kind": "no_finding", "arc_id": "a", "round_n": 3, "producer": "merge-gate-concurrency"},
        {"record_kind": "finding", "finding_type": "HITL-recoverable", "arc_id": "a", "round_n": None, "producer": "merge-door-lease-acquire"},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    out = subprocess.run([sys.executable, "tools/loop_cost_baseline.py", "--log", str(log)], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    assert data["rows"] == 6
    assert data["arcs"] == 1
    assert data["rounds_per_arc_median"] == 3          # the clean round 3 counts; the door row (round_n null) does not
    assert data["gate_rounds_with_findings"] == 1
    assert data["single_lens_rounds"] == 0             # round 2 had two lenses
    assert data["unique_catch_by_producer"] == {"merge-gate-witness-adequacy": 1}   # s1 was rejected
    assert data["unique_catch_rejected"] == 1
    assert data["lease_acquire_events"] == 1
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tools/test_loop_cost_baseline.py -v`
Expected: FAIL, `tools/loop_cost_baseline.py` not found.

- [ ] **Step 3: Write the script**

```python
#!/usr/bin/env python3
"""Loop cost baseline: one JSON object from .harness/merge-gate-log.jsonl.

Read-only. Feeds the §0 table of .harness/plan/loop-optimization-plan-2026-09-03.md.
A round is any (arc_id, round_n) that any record kind names; door rows (round_n null) are
not rounds. A unique catch counts only while no adjudication row rejects its finding_id.
"""
from __future__ import annotations
import argparse, collections, json, statistics, sys
from pathlib import Path

def summarize(rows: list[dict]) -> dict:
    per_arc: dict[str, set] = collections.defaultdict(set)
    by_round: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    rejected = {r.get("finding_id") for r in rows
                if r.get("record_kind") == "finding_adjudication" and r.get("disposition") == "rejected"}
    for r in rows:
        if r.get("round_n") is None:
            continue
        per_arc[r.get("arc_id")].add(r.get("round_n"))
        if r.get("record_kind") == "finding":
            by_round[(r.get("arc_id"), r.get("round_n"))][r.get("producer")] += 1
    is_lens = lambda p: isinstance(p, str) and p.startswith("merge-gate")
    gate_rounds = [k for k, c in by_round.items() if any(is_lens(p) for p in c)]
    single = [k for k in gate_rounds if sum(1 for p in by_round[k] if is_lens(p)) == 1]
    flagged = [r for r in rows if r.get("record_kind") == "finding" and r.get("unique_catch") is True]
    uc = collections.Counter(r.get("producer") for r in flagged if r.get("finding_id") not in rejected)
    return {
        "rows": len(rows),
        "arcs": len(per_arc),
        "rounds_per_arc_median": statistics.median(len(v) for v in per_arc.values()) if per_arc else 0,
        "gate_rounds_with_findings": len(gate_rounds),
        "single_lens_rounds": len(single),
        "unique_catch_by_producer": dict(uc),
        "unique_catch_rejected": sum(1 for r in flagged if r.get("finding_id") in rejected),
        "lease_acquire_events": sum(1 for r in rows if r.get("producer") == "merge-door-lease-acquire"),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=".harness/merge-gate-log.jsonl")
    a = ap.parse_args()
    rows = [json.loads(l) for l in Path(a.log).read_text().splitlines() if l.strip()]
    json.dump(summarize(rows), sys.stdout, indent=2)
    print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test, then the script on the real log**

Run: `uv run pytest tools/test_loop_cost_baseline.py -v && uv run python tools/loop_cost_baseline.py`
Expected: PASS; on the real log, `gate_rounds_with_findings` and `single_lens_rounds` re-derive the §0 rows (48 and 33 at the 2026-09-03 measurement head), `unique_catch_by_producer` re-derives the net figure (19 / 10 / 0 at `02f656c72`), and `lease_acquire_events` is 2. Record the actual numbers at the Task 0 head in §0; a difference is a finding to record, not to explain away.

- [ ] **Step 5: Wire the test into CI parity and commit**

Add `tools/test_loop_cost_baseline.py` to the list in `tools/codex-parity-check.sh` (the `tools/` coverage guard only collects named files). Then:

```bash
git add tools/loop_cost_baseline.py tools/test_loop_cost_baseline.py tools/codex-parity-check.sh
git commit -m "feat(tools): loop_cost_baseline — measured basis for the loop optimization plan"
```
---

### Task 1: CI bookkeeping fast path (largest saving, workspace-ops)

Two of the five CI runs per unit verify a diff that is only `.harness/roadmap_status.md` (the refresh PR and the refresh-merge push); a third, the gate-rows head, is only the two gate-log files but a `pull_request` diff spans the whole PR (see Step 8). Skip the heavy jobs on those diffs at the job level so the required checks still report.

**Files:**
- Modify: `.github/workflows/ci.yml:33-40` (triggers stay), add a `changes` job before line 56, add `needs: changes` + `if:` to the `test`, `coverage`, `axis-isolation`, `typecheck`, and `tools-test-coverage-and-codex-loop` jobs.
- Test: `tools/test_ci_bookkeeping_filter.py` (tests the classifier script, not GitHub).
- Create: `tools/ci_bookkeeping_diff.py`

**Interfaces:**
- Produces: `python tools/ci_bookkeeping_diff.py <base-sha> <head-sha>` prints `bookkeeping=true` when every changed path is in `{.harness/roadmap_status.md, .harness/merge-gate-log.jsonl, .harness/merge-gate-log.md}`, else `bookkeeping=false`. Exit 0 either way; exit 2 if the diff is empty (fail loud, never silently skip).

- [ ] **Step 1: Write the failing test**

```python
# tools/test_ci_bookkeeping_filter.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/test_arc_metrics.py:22 shape — the suite runs --import-mode=importlib (pyproject.toml:383), so sibling modules need tools/ on sys.path explicitly
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

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tools/test_ci_bookkeeping_filter.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write the classifier**

```python
#!/usr/bin/env python3
"""Classify a diff as bookkeeping-only for the CI fast path (Task 1 of the loop optimization plan).

Bookkeeping = only the roadmap status file and/or the two merge-gate log files changed.
An empty diff is an error: the caller must never skip heavy jobs on an unknown diff.
"""
from __future__ import annotations
import subprocess, sys

BOOKKEEPING = frozenset({
    ".harness/roadmap_status.md",
    ".harness/merge-gate-log.jsonl",
    ".harness/merge-gate-log.md",
})

def classify(paths: list[str]) -> bool:
    if not paths:
        raise ValueError("empty diff: refusing to classify")
    return all(p in BOOKKEEPING for p in paths)

def main(argv: list[str]) -> int:
    base, head = argv[1], argv[2]
    out = subprocess.run(["git", "diff", "--name-only", f"{base}..{head}"], capture_output=True, text=True, check=True).stdout
    paths = [p for p in out.splitlines() if p.strip()]
    try:
        flag = classify(paths)
    except ValueError as e:
        print(f"ci_bookkeeping_diff: {e}", file=sys.stderr)
        return 2
    print(f"bookkeeping={'true' if flag else 'false'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run the test**

Run: `uv run pytest tools/test_ci_bookkeeping_filter.py -v`
Expected: 4 passed.

- [ ] **Step 5: Add the `changes` job and gate the heavy jobs**

Insert before the first job in `.github/workflows/ci.yml` (line 56 today):

```yaml
  changes:
    name: classify diff (bookkeeping fast path)
    runs-on: ubuntu-latest
    outputs:
      bookkeeping: ${{ steps.classify.outputs.bookkeeping }}
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4 — the SHA every other job in ci.yml pins (codex r2 on b-230-register: this job decides whether five heavy checks run, so a movable tag here is a bypass)
        with:
          fetch-depth: 0
      - id: classify
        run: |
          set -euo pipefail
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            BASE="${{ github.event.pull_request.base.sha }}"; HEAD="${{ github.event.pull_request.head.sha }}"
          else
            BASE="${{ github.event.before }}"; HEAD="${{ github.sha }}"
          fi
          OUT=$(python3 tools/ci_bookkeeping_diff.py "$BASE" "$HEAD")   # stdlib only; the changes job has no uv setup on purpose (it must finish in seconds)
          echo "$OUT" | tee -a "$GITHUB_OUTPUT"
```

Then on each of `test`, `coverage`, `axis-isolation`, `typecheck`, `tools-test-coverage-and-codex-loop` add:

```yaml
    needs: changes
    if: always() && needs.changes.outputs.bookkeeping != 'true'
```

`always()` is load-bearing: without it a failing `changes` job would mark every dependent job `skipped`, GitHub would report them as Success, and a broken classifier would make pytest disappear from a mergeable PR. With it, a failed classifier leaves the output empty and every heavy job runs.

Leave `lint`, `codex-context-guard`, `arc-ledger`, `substitution-ledger`, `claude-md-citations`, `semantic-overlay`, `q1-review-gate`, `q3-evidence-and-closure-gate`, `split-brain`, `clearance-corpus` unconditional: together they take under a minute and `codex-context-guard` is the check a status-only PR exists to pass.

- [ ] **Step 6: Three witnesses before and after merging the workflow change**

Positive: the Task 1 PR touches `.github/` and `tools/`, so every job must run (`gh pr checks <n>` shows `changes` logging `bookkeeping=false` and pytest running). Negative: on a throwaway branch, make `tools/ci_bookkeeping_diff.py` exit 2 unconditionally and push; pytest must still run (proves the `always()` guard). After merge, the door's next refresh PR is the third witness: `gh pr checks <refresh-pr>` must show pytest, coverage, axis-isolation, typecheck, tools-coverage as `skipped` and the PR mergeable. If any required check shows "Expected" instead of `skipped`, `git revert` and record the finding here; do not widen the filter.

- [ ] **Step 7: Commit**

```bash
git add .github/workflows/ci.yml tools/ci_bookkeeping_diff.py tools/test_ci_bookkeeping_filter.py tools/codex-parity-check.sh
git commit -m "ci: bookkeeping fast path — skip heavy jobs when only roadmap_status or gate-log files change"
```

**Expected saving:** two runs per unit drop from ~455 s to ~60 s: the refresh PR run and the refresh-merge `main` push run (`github.event.before..github.sha` is the refresh commit alone). That is about 13 minutes of wall clock per landed unit, all of it inside the lease, so the door's hold shrinks from about 23 minutes to about 10. The "final head after gate rows" PR run stays full, because a `pull_request` diff is `base..head` and covers the whole PR.

- [ ] **Step 8 (optional, decision-gated): make the gate-rows head run cheap too.** Diffing `github.event.before..github.event.after` on `synchronize` would classify the gate-rows push as bookkeeping and skip pytest on that head. That reinterprets the rule at `.claude/skills/merge-gate/SKILL.md:229-237` ("wait for CI at that final head"): the evidence would come from the previous head plus `merge-gate-landing-delta` proving the delta is only the two log files. It is coherent, but it changes what the rule means, so it goes into the same AskUserQuestion as Task 6 Step 6 with the merge-gate skill edit attached, and is not built before that answer.

---

### Task 2: Prompt hook and banner signal (hooks category)

**Files:**
- Modify: `tools/hooks/lib.sh:267-286` (`hook_roadmap_next`)
- Modify: `tools/hooks/loop_lib.sh` `loop_notify_summary` (line 661), the reducer that renders `NOTIFY` rows into the banner. The emitter (`tools/merge_door.py:1254`) writes one row per landing and is correct; the repeats are rows from successive landings that the reducer renders verbatim (codex r2 on b-230-register).
- Test: `tools/hooks/test_lib_roadmap_next.sh` (bash, same shape as `tools/hooks/test_permission_guard.sh`)

- [ ] **Step 0: Diagnosis (done 2026-09-03, re-run before editing)**

Run: `bash -c 'source tools/hooks/lib.sh; hook_roadmap_next .harness/roadmap_status.md'`
Observed: empty. The live "Current next action (post-#1497)" paragraph names its units without backticks ("U-HE-36 landed as the R3 eval arc … then U-HE-37"), and both existing extraction rules (`tools/hooks/lib.sh:272-276`, `:281-285`) require a backticked `U-`/`R-` token. Cause: the pointer prose stopped quoting unit ids; the parser never accepted unquoted ones.

- [ ] **Step 1: Write the failing test**

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

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tools/hooks/test_lib_roadmap_next.sh`
Expected: `FAIL: unquoted then-tail`.

- [ ] **Step 3: Extend the parser**

In `hook_roadmap_next` (`tools/hooks/lib.sh:267-286`) insert three rules before the existing backticked-token rules, so precedence is: plan pointer; then the first bold `**U-…**`/`**R-…**` token (the pointer prose marks the next unit in bold, as the live post-#1497 paragraph does — "The next implementable unit is **U-HE-37** …, then U-HE-38"); then the unit after the FIRST `then ` (a last-`then` rule returns the successor's successor on exactly that prose — codex r3 on b-230-register); then the existing quoted rules:

```bash
  # Rule 0: a backticked plan pointer wins → plan:<name>
  local plan
  plan=$(printf '%s\n' "$section" | grep -oE '`\.harness/plan/[A-Za-z0-9_.-]+\.md`' | head -1 | sed -E 's#`\.harness/plan/(.*)\.md`#plan:\1#')
  [ -n "$plan" ] && { printf '%s\n' "$plan"; return 0; }
  # Rule 1: the first BOLD unit token — the pointer prose marks "the next implementable unit is **U-…**"
  local bold
  bold=$(printf '%s\n' "$section" | grep -oE '\*\*[UR]-[A-Z]+-[0-9]+\*\*' | head -1 | tr -d '*')
  [ -n "$bold" ] && { printf '%s\n' "$bold"; return 0; }
  # Rule 2: the unit after the FIRST "then " (the ship-pr "then <next unit>" tail), quoted or not.
  # FIRST, not last: "…then U-HE-37 opens, then U-HE-38" names U-HE-37 as next.
  local tail
  tail=$(printf '%s\n' "$section" | grep -oE 'then `?[UR]-[A-Z]+-[0-9]+`?' | head -1 | grep -oE '[UR]-[A-Z]+-[0-9]+')
  [ -n "$tail" ] && { printf '%s\n' "$tail"; return 0; }
```

- [ ] **Step 4: Run the test**

Run: `bash tools/hooks/test_lib_roadmap_next.sh`
Expected: `ok`. Witness on the live file: `bash -c 'source tools/hooks/lib.sh; hook_roadmap_next .harness/roadmap_status.md'` prints the unit the pointer paragraph names as next (the plan pointer once Task 9's refresh installs it; `U-HE-37` for the post-#1497 prose), and a fresh prompt shows the same in `[roadmap] next=`. The test fixtures mirror the live shapes so the suite does not go stale with each refresh.

- [ ] **Step 5: Deduplicate the banner line in the reducer**

In `loop_notify_summary` (`tools/hooks/loop_lib.sh:661`) the reducer promises the NEWEST five (`tail -5` at `:674`), so a `sort -u` before the cap would replace chronology with lexicographic order and could hide a newer notice (codex r4 on b-230-register). Dedupe preserving LAST-occurrence order instead, before the cap — an awk pass that walks the rows backwards keeping the first sighting of each detail and prints them forwards: `awk '{a[NR]=$0} END{for(i=NR;i>0;i--) if(!s[a[i]]++) o[++n]=a[i]; for(i=n;i>0;i--) print o[i]}'` (no `tac`; macOS lacks it). Add `tools/hooks/test_loop_lib_notify.sh` (same shape as `tools/hooks/test_permission_guard.sh`): the same `NOTIFY` detail on three rows renders once; seven distinct details render the newest five in ledger order; a detail repeated at rows 1 and 8 of nine renders once, at row 8's position. Witness: a new session with a `.codex-worktrees/` lane present shows the line once.

- [ ] **Step 6: Commit**

```bash
git add tools/hooks/lib.sh tools/hooks/test_lib_roadmap_next.sh tools/hooks/loop_lib.sh tools/hooks/test_loop_lib_notify.sh
git commit -m "fix(hooks): prompt-context next= recognizes plan pointers; dedupe worktree lane notice"
```

---

### Task 3: One-invocation arc close-out (serial tail)

The close-out after the door releases is eight serial steps (`.claude/skills/ship-pr/SKILL.md:387-644`). Reflect and `/context-save-lean` need the session; the exit report, metrics queue, and deferral rows do not. Fold those three into one recipe. The queue half keeps `arc-metrics queue`'s own contract — `--transcript` is omitted when no transcript matches unambiguously and `--levers` is zero or many separate tokens (`ship-pr/SKILL.md:587-602`; `tools/arc_metrics.py` declares `--levers` with `nargs="*"`) — so the recipe forwards everything after its three exit-report positionals verbatim instead of naming them (codex r1 on b-230-register: fixed positionals could not express a valid close-out).

**Files:**
- Modify: `justfile` (add `arc-close` next to `arc-exit-report` at line 265; the justfile sets `positional-arguments` and no `shell`, so each line runs under `sh -cu` — POSIX only, no `${@:4}` (codex r2 on b-230-register))
- Modify: `.claude/skills/ship-pr/SKILL.md:541-624` (replace the two separate invocations with `just arc-close`)
- Test: `tools/test_arc_close_recipe.py`

- [ ] **Step 1: Write the failing test** (the recipe EXECUTES; the inner `just` calls are captured by a shim ahead of the real binary on `PATH`, so the shell's positional handling is exercised, not printed — `just -n` would not expand `$@`)

```python
# tools/test_arc_close_recipe.py
import os, shutil, subprocess, sys

def _run(tmp_path, *args):
    shim = tmp_path / "bin"; shim.mkdir()
    log = tmp_path / "calls.txt"
    (shim / "just").write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> {log}\n")
    (shim / "just").chmod(0o755)
    real = shutil.which("just")
    env = {**os.environ, "PATH": f"{shim}{os.pathsep}{os.environ['PATH']}"}
    p = subprocess.run([real, "arc-close", *args], capture_output=True, text=True, env=env)
    return p.returncode, log.read_text().splitlines() if log.exists() else []

def test_forwards_full_queue_tail(tmp_path):
    rc, calls = _run(tmp_path, "12", "abc123", "cp.md", "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
                     "--round-logs", "logs/*.log", "--transcript", "t.jsonl", "--levers", "B-1", "B-2")
    assert rc == 0
    assert calls == [
        "arc-exit-report --pr 12 --merge-sha abc123 --checkpoint cp.md",
        "arc-metrics queue --pr 12 --arc-id u-x --arc-type applying --decisions 0 --round-logs logs/*.log --transcript t.jsonl --levers B-1 B-2",
    ]

def test_omitting_transcript_and_levers_is_representable(tmp_path):
    rc, calls = _run(tmp_path, "12", "abc123", "cp.md", "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0", "--round-logs", "logs/*.log")
    assert rc == 0
    assert calls[1] == "arc-metrics queue --pr 12 --arc-id u-x --arc-type applying --decisions 0 --round-logs logs/*.log"
```

The glob survives because `positional-arguments` hands each argument through `"$@"` unexpanded; the shim proves it.

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tools/test_arc_close_recipe.py -v`
Expected: FAIL (unknown recipe).

- [ ] **Step 3: Add the recipe**

```just
# Loop optimization plan Task 3: the non-interactive close-out tail in one call. Three
# positionals feed arc-exit-report; everything after them is arc-metrics queue's own
# argument list, forwarded verbatim (POSIX `shift 3` then "$@" — the recipe shell is `sh -cu`) so its contract is unchanged:
# omit --transcript when ambiguous, pass zero or many --levers tokens. Each line runs in
# its own shell and just stops at the first non-zero exit.
arc-close pr merge_sha checkpoint *QUEUE_ARGS:
    just arc-exit-report --pr "$1" --merge-sha "$2" --checkpoint "$3"
    pr="$1"; shift 3; just arc-metrics queue --pr "$pr" "$@"
```

- [ ] **Step 4: Run the test**

Run: `uv run pytest tools/test_arc_close_recipe.py -v`
Expected: 2 passed.

- [ ] **Step 5: Update ship-pr**

In `.claude/skills/ship-pr/SKILL.md` §"Arc exit report" and §"Arc-metrics capture", replace the two command blocks with the single `just arc-close <pr> <merge-sha> <checkpoint> --arc-id … --arc-type … --decisions … --round-logs … [--transcript …] [--levers …]` invocation and keep the surrounding rules (skip when the PR was itself the refresh; queue writes outside the repo; the transcript and lever rules stay exactly as written). Run `just codex-check` (the docs and citation gates read skill files).

- [ ] **Step 6: Commit**

```bash
git add justfile .claude/skills/ship-pr/SKILL.md tools/test_arc_close_recipe.py tools/codex-parity-check.sh
git commit -m "feat(just): arc-close folds exit-report + metrics queue into one close-out call"
```

Leave the cross-arc metrics drain as it is. Its reason is durability (`ship-pr/SKILL.md:604-611`, `justfile:232-234`): a row is released only once it is in merged history, and a topic worktree must never be left dirty. That is a correct constraint, not waste.
---

### Task 4: Batched branch hygiene (one approval instead of N)

The parser and the producer must agree on one row shape (codex r1 on b-230-register: the skill's canonical defer text, `ship-pr/SKILL.md:479`, carries only `<branch>`, while the rows the loop actually wrote carry `<branch> (PR #N, merged <sha>, main run green)` pairs; a parser built for the richer shape would find nothing in a row written from the skill text). This task makes the richer shape canonical in the skill and makes the parser refuse, loudly, any pending row it cannot read.

**Files:**
- Create: `tools/branch_hygiene_batch.py`
- Modify: `justfile` (add `branch-hygiene-pending`)
- Modify: `.claude/skills/ship-pr/SKILL.md:471-480` (the canonical defer text carries the PR pairs; the deferral text points at the batch recipe)
- Test: `tools/test_branch_hygiene_batch.py`

**Interfaces:**
- Produces: `python tools/branch_hygiene_batch.py --pending <loop_status.md>` prints one line per verified-merged branch as `<branch> <head_oid>` and, with `--emit-command`, prints the single guarded push:
  `git push --force-with-lease=refs/heads/A:<oidA> --force-with-lease=refs/heads/B:<oidB> origin :refs/heads/A :refs/heads/B`
  Two phases, each rerunnable on its own. Phase 1 (`--emit-command`) prints the guarded push. Phase 2 (`--resolve`, recipe `branch-hygiene-resolve`) is run AFTER the push: for each deferral it confirms every branch is absent on the remote (`git ls-remote --exit-code --heads origin refs/heads/<b>` exit 2 — the one "genuinely absent" signal ship-pr already uses; any other non-zero aborts) and only then appends the `RESOLVED-HIL` row through `loop_resolve <item-id> …` (`tools/hooks/loop_lib.sh:286`), because the pending reducer is last-write-wins on the item id and a deletion without its resolve row is re-presented forever (codex r3 on b-230-register). Keying the resolve on the remote's state rather than on the push having just run makes it retryable: if one append fails, rerunning `--resolve` skips nothing that is still present and resolves everything that is gone, without re-issuing a force-with-lease against OIDs that no longer exist (codex r4 on b-230-register). Item ids are validated against `[A-Za-z0-9._-]+` at parse time and every value that reaches a shell is `shlex.quote`d — a ledger token is shared, append-only data, not trusted program text (codex r4 on b-230-register, P1). A pending row with no `<branch> (PR #N, merged` pair is printed to stderr as `unreadable pending row: <row>` and makes the exit non-zero; it is never skipped silently. A branch whose PR is not `MERGED` or whose head branch differs aborts the whole batch (exit 1, `verification mismatch: <branch> PR #N: <reason>` on stderr, no command printed): a partially stale queue must never become a partially executed destructive push (codex r2 on b-230-register). Input is the loop's pending-HIL reducer (`loop_pending_hil_list`, `tools/hooks/loop_lib.sh:392`, last-write-wins so a `RESOLVED-HIL` row clears its item), read from stdin — never the raw ledger, which would resurrect resolved rows — and the ledger path is the canonical `loop_status_path()` (`loop_lib.sh:31`), which honours alternate venues.

- [ ] **Step 1: Write the failing test**

```python
# tools/test_branch_hygiene_batch.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/test_arc_metrics.py:22 shape — the suite runs --import-mode=importlib (pyproject.toml:383), so sibling modules need tools/ on sys.path explicitly
import pytest
from branch_hygiene_batch import Deferral, build_push_command, parse_pending, resolve_cleared, UnreadableRow

def test_two_branches_one_command():
    cmd = build_push_command([("feat/a", "aaa111"), ("roadmap-refresh-post-1", "bbb222")])
    assert cmd == ("git push --force-with-lease=refs/heads/feat/a:aaa111 "
                   "--force-with-lease=refs/heads/roadmap-refresh-post-1:bbb222 "
                   "origin :refs/heads/feat/a :refs/heads/roadmap-refresh-post-1")

def test_empty_list_is_an_error():
    with pytest.raises(ValueError):
        build_push_command([])

def test_parse_pending_row_finds_both_branches():
    row = ("[lane-1] u-sr-08 — branch hygiene close-out pending: feat/u-sr-08-context-noise-deletions "
           "(PR #1489, merged 9032fead4, main run green) and roadmap-refresh-post-1489 "
           "(PR #1490, merged ff62189d2, main run green) — run the guarded force-with-lease delete block")
    assert parse_pending(row) == [Deferral("u-sr-08", [("feat/u-sr-08-context-noise-deletions", "1489"), ("roadmap-refresh-post-1489", "1490")])]

def test_crafted_item_id_is_refused():
    with pytest.raises(UnreadableRow):
        parse_pending("[lane-1] $(touch pwned) — branch hygiene close-out pending: feat/a (PR #1, merged 111, main run green)")

def test_resolve_only_items_whose_branches_are_all_gone(monkeypatch):
    import branch_hygiene_batch as m
    gone = {"feat/a": True, "roadmap-refresh-post-1": True, "feat/b": False}
    monkeypatch.setattr(m, "remote_absent", lambda branch: gone[branch])
    resolved = []
    monkeypatch.setattr(m, "loop_resolve", lambda item, note: resolved.append((item, note)))
    left = resolve_cleared([Deferral("u-a", [("feat/a", "1"), ("roadmap-refresh-post-1", "2")]), Deferral("u-b", [("feat/b", "3")])])
    assert [i for i, _ in resolved] == ["u-a"]
    assert left == [Deferral("u-b", [("feat/b", "3")])]

def test_bare_branch_row_is_refused_not_skipped():
    with pytest.raises(UnreadableRow):
        parse_pending("[lane-1] u-x — branch hygiene close-out pending: feat/u-x — run the guarded block")

def test_one_mismatch_aborts_the_batch(monkeypatch):
    import branch_hygiene_batch as m
    monkeypatch.setattr(m, "pr_view", lambda pr: {"state": "MERGED", "headRefName": "feat/a" if pr == "1" else "other", "headRefOid": "aaa"})
    with pytest.raises(m.VerificationMismatch):
        m.verify_all([Deferral("u-a", [("feat/a", "1")]), Deferral("u-b", [("feat/b", "2")])])
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tools/test_branch_hygiene_batch.py -v`
Expected: FAIL, import error.

- [ ] **Step 3: Write the tool**

```python
#!/usr/bin/env python3
"""Batch the deferred branch-hygiene deletions into ONE guarded push (Task 4).

Reads the 'branch hygiene close-out pending' rows the loop deferred, verifies each PR is MERGED and
its head OID still matches (the same checks ship-pr runs one branch at a time), and prints a single
`git push --force-with-lease=... origin :refs/heads/...` that deletes all of them. The push itself is
still typed by the operator in an interactive session: the permission guard denies force pushes to
the loop, by design. This tool only collapses N approvals into one.

Row shape (the ONE shape: ship-pr's defer text produces it, the pending reducer renders it, this reads it):
  [<lane>] <item-id> — branch hygiene close-out pending: <branch> (PR #N, merged <sha>, main run green)[ and <branch> (PR #M, ...)]
A pending row without a `<branch> (PR #N, merged` pair is unreadable and is refused, never skipped.
Phase 1 (--emit-command) prints the push. Phase 2 (--resolve) appends one RESOLVED-HIL row per item
whose branches are ALL absent on the remote — the pending reducer is last-write-wins on the item id, so
a deletion without its resolve row stays pending forever. Phase 2 is keyed on the remote's state, so it
is safe to rerun after a partial failure. Ledger tokens are data: item ids are validated at parse time
and every value handed to a shell is shlex-quoted.
"""
from __future__ import annotations
import argparse, json, re, shlex, subprocess, sys
from dataclasses import dataclass

PENDING = re.compile(r"\[[^\]]*\] (?P<item>[A-Za-z0-9._-]+) — branch hygiene close-out pending: (?P<rest>.*)")
BRANCH = re.compile(r"(?P<branch>[\w./-]+) \(PR #(?P<pr>\d+), merged")

class UnreadableRow(ValueError):
    """A pending row that names no `<branch> (PR #N, merged` pair."""

@dataclass(frozen=True)
class Deferral:
    item_id: str
    branches: list[tuple[str, str]]   # (branch, pr) — the content branch AND its refresh branch

def parse_pending(text: str) -> list[Deferral]:
    out: list[Deferral] = []
    for line in text.splitlines():
        if "branch hygiene close-out pending:" not in line:
            continue
        m = PENDING.search(line)
        if m is None:
            raise UnreadableRow(line)          # an item id outside [A-Za-z0-9._-]+ is unreadable, not shell input
        pairs = [(b.group("branch"), b.group("pr")) for b in BRANCH.finditer(m.group("rest"))]
        if not pairs:
            raise UnreadableRow(line)
        out.append(Deferral(m.group("item"), pairs))
    return out

def build_push_command(branches: list[tuple[str, str]]) -> str:
    if not branches:
        raise ValueError("no verified branches to delete")
    leases = " ".join(f"--force-with-lease=refs/heads/{b}:{oid}" for b, oid in branches)
    refs = " ".join(f":refs/heads/{b}" for b, _ in branches)
    return f"git push {leases} origin {refs}"

class VerificationMismatch(RuntimeError):
    """One branch failed verification; the whole batch is refused (no partial destructive push)."""

def pr_view(pr: str) -> dict:
    return json.loads(subprocess.run(["gh", "pr", "view", pr, "--json", "state,headRefName,headRefOid"], capture_output=True, text=True, check=True).stdout)

def verify_all(deferrals: list[Deferral]) -> dict[str, str]:
    """branch -> verified head OID for every branch of every deferral; the FIRST mismatch refuses the batch."""
    out: dict[str, str] = {}
    for d in deferrals:
        for branch, pr in d.branches:
            info = pr_view(pr)
            if info["state"] != "MERGED":
                raise VerificationMismatch(f"{branch} PR #{pr}: state {info['state']}, not MERGED")
            if info["headRefName"] != branch:
                raise VerificationMismatch(f"{branch} PR #{pr}: head branch is {info['headRefName']}")
            out[branch] = info["headRefOid"]
    return out

def remote_absent(branch: str) -> bool:
    """True only on ls-remote exit 2 (the ref is gone); any other non-zero is an error, never 'gone'."""
    p = subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", f"refs/heads/{branch}"], capture_output=True, text=True)
    if p.returncode == 0:
        return False
    if p.returncode == 2:
        return True
    raise RuntimeError(f"ls-remote {branch}: exit {p.returncode}: {p.stderr.strip()}")

def loop_resolve(item_id: str, note: str) -> None:
    """Append the RESOLVED-HIL row through the ledger's one writer; every value is shell-quoted."""
    cmd = f"source tools/hooks/loop_lib.sh; loop_resolve {shlex.quote(item_id)} {shlex.quote(note)}"
    subprocess.run(["bash", "-c", cmd], check=True)

def resolve_cleared(deferrals: list[Deferral]) -> list[Deferral]:
    """Resolve every deferral whose branches are ALL absent; return the ones still pending."""
    left: list[Deferral] = []
    for d in deferrals:
        if all(remote_absent(b) for b, _ in d.branches):
            loop_resolve(d.item_id, "branch hygiene done: " + ", ".join(b for b, _ in d.branches) + " absent on origin (just branch-hygiene-resolve)")
        else:
            left.append(d)
    return left

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending", required=True, help="pending-HIL reducer output; '-' reads stdin")
    ap.add_argument("--emit-command", action="store_true", help="phase 1: print the ONE guarded push")
    ap.add_argument("--resolve", action="store_true", help="phase 2: resolve every item whose branches are gone on origin")
    a = ap.parse_args()
    text = sys.stdin.read() if a.pending == "-" else open(a.pending).read()
    try:
        deferrals = parse_pending(text)
    except UnreadableRow as e:
        print(f"unreadable pending row: {e}", file=sys.stderr)
        return 2
    if a.resolve:
        left = resolve_cleared(deferrals)
        for d in left:
            print(f"still present: {d.item_id} {' '.join(b for b, _ in d.branches)}")
        return 0 if not left else 1
    try:
        oids = verify_all(deferrals)
    except VerificationMismatch as e:
        print(f"verification mismatch: {e}", file=sys.stderr)
        return 1
    for b, oid in oids.items():
        print(f"{b} {oid}")
    if a.emit_command:
        print(build_push_command(list(oids.items())))
        print("# then, once the push has run:  just branch-hygiene-resolve", file=sys.stderr)
    return 0 if oids else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test**

Run: `uv run pytest tools/test_branch_hygiene_batch.py -v`
Expected: 7 passed.

- [ ] **Step 5: Recipe and skill text**

```just
# Task 4: list verified-merged deferred branches and print the ONE guarded delete to run by hand.
# The input is the pending-HIL REDUCER (last-write-wins; a RESOLVED-HIL row clears its item)
# over the canonical loop_status_path() venue — never the raw ledger.
branch-hygiene-pending:
    bash -c 'source tools/hooks/loop_lib.sh; loop_pending_hil_list' | uv run python tools/branch_hygiene_batch.py --pending - --emit-command

# Phase 2, after the push: resolve every deferral whose branches are gone on origin. Rerunnable.
branch-hygiene-resolve:
    bash -c 'source tools/hooks/loop_lib.sh; loop_pending_hil_list' | uv run python tools/branch_hygiene_batch.py --pending - --resolve
```

In `ship-pr/SKILL.md:471-480`, replace the canonical defer text with the one shape the parser reads — `bash tools/04-loop/defer.sh <arc-id> "branch hygiene close-out pending: <branch> (PR #<N>, merged <merge-sha>, main run green) and roadmap-refresh-post-<N> (PR #<refresh-N>, merged <refresh-merge-sha>, main run green)"` — and after it add: "In the next interactive session run `just branch-hygiene-pending`, paste the printed push (one approval clears every verified row), then run `just branch-hygiene-resolve` — it appends the `RESOLVED-HIL` row for each item whose branches are gone on origin, which is what makes the reducer stop presenting them; it is safe to rerun." The parser docstring and this skill sentence are the two carriers of the shape; `parse_pending` is the authority.

- [ ] **Step 6: Witness and commit**

Run `just branch-hygiene-pending` against the current three deferrals; expected: six `branch oid` lines (each row names a content branch and its refresh branch) and one push command; `just branch-hygiene-resolve` run BEFORE the push must report all three items `still present` and resolve nothing. Do not run the push inside this task's PR; the operator runs it, then the resolve recipe, and the witness that the deferrals stop re-surfacing is the next session's banner. Then:

```bash
git add tools/branch_hygiene_batch.py tools/test_branch_hygiene_batch.py justfile .claude/skills/ship-pr/SKILL.md tools/codex-parity-check.sh
git commit -m "feat(tools): branch_hygiene_batch — one guarded push for all deferred deletions"
```
---

### Task 5: Merge-gate emit in one call (smaller items)

Today the gate publishes three bindings, then emits three verdicts, each as its own `just` call (`merge-gate/SKILL.md:74-87,171-195`). `merge-gate-emit` exits 1 for a *recorded* BLOCK and 2 for a verdict that was NOT recorded (`justfile:354-355`), so a multi-line just recipe would stop after a recorded BLOCK and leave the later lenses unrecorded — a breach of the all-three-verdicts audit contract (codex r1 on b-230-register). The loop therefore lives in Python, where a recorded BLOCK is a result, not an abort.

**Files:**
- Modify: `tools/merge_gate_log.py`: add an `emit-all` subcommand taking `--pr`, `--arc-id`, `--concurrency-json`, `--spec-json`, `--witness-json` (plus the `emit` flags it forwards), which runs the existing `emit` path for each lens in the fixed order and exits with the worst code (2 if any verdict was not recorded, else 1 if any recorded BLOCK, else 0). It is resumable: before emitting a lens it reads the JSONL for a verdict row already recorded for `(arc_id, head_sha, producer=merge-gate-<lens>)` — the identity a gate row actually carries (`arc_id`, `head_sha`, `producer`; there is no `pr` field on the JSONL row, the Markdown sibling is the PR authority, codex r4 on b-230-register) — and skips that lens with `already recorded`, so a re-run after one lens returned 2 emits only the lens that failed and never duplicates an earlier emission (codex r3 on b-230-register).
- Modify: `justfile`: add `merge-gate-emit-all *ARGS` forwarding to the subcommand, next to `merge-gate-emit` (line 359).
- Modify: `.claude/skills/merge-gate/SKILL.md:171-195` to call it.
- Test: `tools/test_merge_gate_emit_all.py`.

- [ ] **Step 1: Write the failing test.** Monkeypatch the single-emit function to return 1 for `merge-gate-concurrency` and 0 for the other two, record the calls; assert all three lenses were emitted in the order `merge-gate-concurrency`, `merge-gate-spec-conformance`, `merge-gate-witness-adequacy` and the exit is 1. Second case: the middle lens returns 2; assert the third lens is still emitted and the exit is 2. Third case (resume): against a temp JSONL that already holds verdict rows for the first two lenses at this `(arc_id, head_sha)` — rows in the real row shape, `arc_id`/`head_sha`/`producer`/`record_kind`, no `pr` — assert only `merge-gate-witness-adequacy` is emitted, the log gains exactly one row, and the exit is that lens's code. Fourth case: `just --show merge-gate-emit-all` names the subcommand.
- [ ] **Step 2: Run it, expect FAIL.**
- [ ] **Step 3: Add the subcommand and the recipe**

```just
# All three lens verdicts in one call, fixed order, NEVER stopping at a recorded BLOCK
# (exit 1 is a recorded verdict, not a failure): exit = worst of the three emits.
#   just merge-gate-emit-all --pr <N> --arc-id <arc-id> --concurrency-json <f> --spec-json <f> --witness-json <f>
merge-gate-emit-all *ARGS:
    uv run python tools/merge_gate_log.py emit-all "$@"
```

- [ ] **Step 4: Run the test, expect PASS.**
- [ ] **Step 5: Wire `tools/test_merge_gate_emit_all.py` into `tools/codex-parity-check.sh`** (the `tools/` coverage guard rejects any unexecuted `tools/test_*.py`; codex r4 on b-230-register), update the skill text, and commit with `git commit -m "feat(just): merge-gate-emit-all"`.

The second disjointness check at ship time stays: HEAD changed since selection, so it is not a duplicate.
---

### Task 6: Concurrency lens on demand (duplicate reviews, spec-gated)

Basis: the concurrency lens has 1 raw / 0 net unique catches in 88 findings; witness-adequacy has 22 raw / 19 net and spec-conformance 10 (§0). Running the concurrency lens only when the diff touches a shared-state or process-isolation surface removes one subagent from the gate rounds the detector clears; Step 5 measures how many that is. Running fewer lenses is what C-HE-34 forecloses — "No collapsing of review layers to cut the 68%" (`Spec_HE_Loop_Lanes_v1.md:823`) — so an operator answer cannot enable it directly (codex r1 on b-230-register): Steps 1–5 build the detector and the measurement (mode-agnostic), Step 6 asks once, and a *yes* opens a spec leg (a change note qualifying C-HE-34 for a detector-gated lens, clearance marker, HE plan update, landed as a doc-only PR) before the skill edit lands. Spec versions are allocated serially at the moment a leg opens — the next number after the cleared head at that time (v1.8 while v1.7 is the head) — never pre-assigned here, since Tasks 6, 7 and 8 may each be accepted (codex r2 on b-230-register).

**Files:**
- Create: `tools/concurrency_surface.py`
- Test: `tools/test_concurrency_surface.py`
- Modify (only after the spec leg is cleared): `.claude/skills/merge-gate/SKILL.md:110-169` and `:197-219`.

The detector reads the **diff**, not the surviving files: a deleted file, a removed lock, and a shell or workflow change are exactly the changes for which skipping the lens is unsafe, and none of them is visible in the post-change contents of existing `.py` files (codex r1 on b-230-register). It scans added and removed lines of every path.

- [ ] **Step 1: Write the failing test**

```python
# tools/test_concurrency_surface.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/test_arc_metrics.py:22 shape — the suite runs --import-mode=importlib (pyproject.toml:383), so sibling modules need tools/ on sys.path explicitly
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
- [ ] **Step 3: Write the detector**

```python
#!/usr/bin/env python3
"""Does a diff touch a concurrency surface? (Task 6 of the loop optimization plan.)

Input is unified-diff text (`git diff -U0 <base>..<head>`); added AND removed lines of every
path are scanned, so a deleted file, a removed lock, and a shell/workflow change all count.
Input with no content lines (an empty or failed diff, a binary-only change) is UNKNOWN and
exits 2: the caller runs the lens on any non-zero exit (codex r4 on b-230-register).
"""
from __future__ import annotations
import re, sys

PATTERN = re.compile(r"\b(asyncio\.(gather|create_task|Lock|Semaphore|Queue|timeout|wait_for|shield)|CancelledError|\.cancel\(|TimeoutError|threading|multiprocessing|concurrent\.futures|fcntl|flock|os\.link|O_EXCL|subprocess\.Popen|Lock\(|Semaphore\(|\.exists\(\)|\.is_file\(\)|os\.path\.exists|\.unlink\(|os\.remove|os\.rename|os\.replace|\bglobal |\bnonlocal )")
# Deliberately not `await ` or bare `asyncio`: nearly every harness diff is async. This is a token
# ALLOWLIST and therefore fail-OPEN by construction: a concurrency surface it does not name (a
# check-then-act sequence spelled without these calls, a shared dict mutated through a method) reads
# as `false` and would skip the lens. The tokens cover every construct the lens prompt names
# (`.claude/skills/merge-gate/SKILL.md:110-169`) plus the path-TOCTOU and module-global shapes; the
# residual fail-open set is the risk Step 5 measures and the Step 6 spec leg must state as its bound.

class EmptyDiff(ValueError):
    """No added or removed content lines: a failed or binary-only diff is UNKNOWN, never 'no surface'."""

def touches_concurrency(diff: str) -> bool:
    changed = [l[1:] for l in diff.splitlines() if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    if not changed:
        raise EmptyDiff("no +/- content lines")
    return any(PATTERN.search(l) for l in changed)

if __name__ == "__main__":
    try:
        print("concurrency=" + ("true" if touches_concurrency(sys.stdin.read()) else "false"))
    except EmptyDiff as e:
        print(f"concurrency_surface: {e}: run the lens", file=sys.stderr)
        raise SystemExit(2)
```

- [ ] **Step 4: Run the test, expect PASS. Wire `tools/test_concurrency_surface.py` into `tools/codex-parity-check.sh`** (same coverage-guard rule as Task 5), then commit `git commit -m "feat(tools): concurrency_surface detector (merge-gate lens gating, spec leg pending)"`.
- [ ] **Step 5: Measure on history** — for the last 20 gate rounds, run the detector on each PR's `git diff -U0 base..head` and record how many rounds would have skipped the lens and whether any of the lens's 88 findings (the net-unique count is 0, so the question is whether any *accepted* finding would have been lost) fell in a skipped round. Any accepted concurrency finding in a round the detector would have skipped is a measured instance of the fail-open bound above; record it by finding id. Put the table in this plan under §0.
- [ ] **Step 6: One AskUserQuestion** with the table and the fail-open bound stated: (a) open the C-HE-34 spec leg for a detector-gated concurrency lens — the skill step skips the lens ONLY on a literal `concurrency=false` from the detector; exit 2 (unknown input) and any other failure run the lens — with a typed skip path so C-HE-29 accounting stays whole — `merge_gate_log.py emit --lens merge-gate-concurrency --skipped-reason "no concurrency surface"` writes a `no_finding` row with `finding_type: lens_skipped` and `cause_attribution: detector_no_surface` (the existing `emit` parses only a bound reviewer verdict and records APPROVE as `clean_approve`, so a skip cannot ride it without fabricating reviewer output; the typed path and its tests are part of the code PR — codex r3 on b-230-register); (b) keep three lenses always. On (a): spec + marker PR first (doc-only), then the code PR (typed skip path + tests) and the skill edit. On (b): Steps 1–5 stay as a measurement instrument and this task closes.

The Codex re-run after a lens BLOCK stays. A fix is new code and the out-of-family reviewer has never seen it; the log shows 2039 Codex rows for 343 lens rows, so the re-run is where the catches are.
---

### Task 7: Spec leg — `--delete-branch` in the fixed merge string (optional, policy change)

Deleting the topic branch inside the door removes the deferral queue Task 4 batches. It conflicts with the standing rule that branch deletion is a per-instance human decision (`ship-pr/SKILL.md:471-480`). Offer it; do not build it unless the operator changes the rule.

The permission guard is not on the path (codex r1 on b-230-register, P1): the door runs `gh pr merge` from a Python subprocess inside `tools/merge_door.py`, which the Bash PreToolUse guard never sees, so no allowlist carve-out is needed and the two guard tests that deny the raw verbs — `gh pr merge … --delete-branch` at `tools/hooks/test_permission_guard.sh:174` and `gh pr close … --delete-branch` at `:279` — stay exactly as they are. Allowing the raw merge would bypass the lease-enforcing wrapper; the close verb is unrelated destructive behaviour. Both remain denied under every outcome of this task.

**Files (only after the decision):**
- Modify: `.harness/spec/Spec_HE_Loop_Lanes_v1.md:294` (C-HE-06 §4 iv) and `:334-338` (C-HE-07 §1), bump to the next unallocated version at the time the leg opens (v1.8 if it opens first; the number after any leg cleared before it), with a change note.
- Create: `.harness/clearance/spec-he-loop-lanes-v<that version>-cleared-<date>.md`
- Modify: `tools/merge_door.py:896` (the fixed string), `tools/hooks/safe-merge.sh:2-4` (its comment quoting the string), `.harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md`, and `tools/test_merge_door.py` (the fixed-string witness). No permission-guard or guard-test change.

- [ ] **Step 1:** Present the decision in the same AskUserQuestion as Task 6 Step 6, recommending **no** for now: Task 4 already collapses the cost to one approval per session, and the rule exists because deletion is irreversible.
- [ ] **Step 2 (only on yes):** file the spec change note, land the spec + marker PR first (doc-only, no code, so the context guard's DESIGN_IMPL_MIX rule stays clean), then land the code PR with the four file edits above.
---

### Task 8: Spec leg — lease scope and N-merge refresh (deferred, trigger-gated)

Releasing the lease after the content merge and letting one refresh cover N merges would end serialization, but it needs three coupled changes: C-HE-06 invariants (`Spec_HE_Loop_Lanes_v1.md:317-321`), the §12.2.1 one-commit fixed point in root `CLAUDE.md`, and `_owed_lag` in `tools/codex_context_guard.py:443-469`. The data cannot justify it yet, in either direction: the only `merge-door-lease-acquire` row the door writes is the budget-exhausted one (`tools/merge_door.py:1965`, `lease_acquire_budget_exhausted`, after twelve backoffs of up to ten minutes). A yield that resolves inside the budget writes nothing, so "2 rows in 65 arcs" counts hour-long stalls, not contention. Task 1 cuts the hold from about 23 minutes to about 10 regardless.

- [ ] **Step 1: Make contention visible — out of the repo.** A row appended to the tracked `.harness/merge-gate-log.jsonl` while `wait_for_door` is running lands *after* the PR's final committed head and CI gate; when contention clears the door merges the committed head and the row is left as dirty, unmerged worktree state that blocks cleanup and never reaches durable history (codex r1 on b-230-register; the u-he-36 `refresh_pr_ci_not_green` row this registration PR had to carry is the same defect on the door's post-merge path). The yield therefore goes to the shared, append-only, out-of-repo `loop_status.md` through the writer the door already uses for its `DEFERRED-HIL` rows — `_notify` (`tools/merge_door.py:986`) over `reservations.emit_loop_row` (`tools/reservations.py:750`): at the point where `wait_for_door` first observes `held` (the caller-side backoff near `:1714`) — and ONLY at that first observation, backoff index 0, never on the later retries of the same call — emit one `NOTIFY` row with cause `merge-door-lease-acquire:lease_held_yield` and detail `holder=<holder arc id> backoff=0`. One contention event is one row; an emitter that wrote on every retry would inflate the Step 2 trigger by up to eleven rows per event (codex r3 on b-230-register). This adds a loop-status row; it does not touch acquire, release, the gate log, or the invariants at `Spec_HE_Loop_Lanes_v1.md:317-321`. Test: `tools/test_merge_door.py` gains one case driving `wait_for_door` through three `held` observations before success (patched `sleep`, patched `emit_loop_row` recording every call) and asserting exactly ONE row was emitted, with kind `NOTIFY`, cause exactly `merge-door-lease-acquire:lease_held_yield`, detail containing the holder's arc id and `backoff=0`, and the tracked gate log byte-identical before and after.
- [ ] **Step 2:** Register a forward-register row (the id after Task 9's umbrella, `B-231` if nothing else lands first) titled "Merge-door lease released after content merge; refresh covers N merges", with the trigger "more than 5 `lease_held_yield` rows in any 30-day window after Task 1 lands" and the three cites above.
- [ ] **Step 3:** Extend `tools/loop_cost_baseline.py` with `--loop-status PATH` counting `lease_held_yield` NOTIFY rows, re-run it at each roadmap refresh; when the trigger fires, open the spec leg as a Class 2 decision with a proposed text at the next unallocated version (serial allocation, as for Tasks 6 and 7).
---

### Task 9: Register the plan so the loop can find it (do this first)

`roadmap-continue` derives the next action from `.harness/roadmap_status.md` and `.harness/forward-register.yaml` (root `CLAUDE.md` §12.4.1). An unregistered plan is parked.

**Files:**
- Modify: `.harness/forward-register.yaml` (append one umbrella row; bump `snapshot:` in the same commit, as every row addition does)
- Modify: `.harness/.next-action-draft` (gitignored; consumed by the door's next refresh)

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
    a merge-door lease held across two of them, 33 of 48 gate rounds raised by a single
    lens, and a prompt hook printing next=? because the pointer prose stopped quoting
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

- [ ] **Step 3: Land it** as a doc-only PR (`register`, `snapshot`, this plan file); `just check` green; no merge-gate (no code surface); commit `ops: register B-230 loop optimization program`.

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

## Self-review

- Registration: Task 9 first, so the loop derives the next task instead of parking the plan.
- Coverage: CI runs → Task 1; serialization → Task 1 (duration) + Task 8 (trigger); duplicate reviews → Task 6 (gated) with the Codex re-run kept; hooks → Task 2 (the two real defects); close-out tail and cross-arc coupling → Task 3 (tail) with the coupling left in place for a stated reason; smaller items → Tasks 4 and 5, disjointness check kept.
- No task edits the fixed merge string, releases the lease early, drops the CI-at-final-head rule, or runs fewer review lenses without a spec leg (C-HE-06, C-HE-07, C-HE-34); no task touches the permission guard's denial of the raw `gh pr merge` / `gh pr close --delete-branch` verbs.
- Codex r4 (head `4ff4006ac`) found eight more — a ledger item id interpolated unquoted into `bash -c` (P1; now: id validated at parse, every shell value `shlex.quote`d, and the resolve phase runs in-process rather than as pasted text), a push-then-resolve block that could not be rerun after a partial failure (now: two rerunnable phases, resolve keyed on the remote's absence), `sort -u` reordering the newest-five notify cap (now: last-occurrence dedupe before the cap), a resume key naming a `pr` field the JSONL row does not carry (now: `arc_id`/`head_sha`/`producer`), a detector that read an empty or binary diff as "no surface" (now: `EmptyDiff`, exit 2, lens runs), bare sibling imports the importlib suite rejects (now: the `sys.path` shape every tools test uses), two new tools tests left out of the parity list (now: wired), and an umbrella close_out that could close before the trigger existed (now: Task 8 Steps 1-3) — all absorbed, each marked "codex r4 on b-230-register".
- Codex r3 (head `034b392ee`) found seven more — a last-`then` rule that returned U-HE-38 on the live prose (now: bold token first, then the FIRST then-tail), a batch that deleted branches but never appended the `RESOLVED-HIL` rows the last-write-wins reducer needs (now: one block, push `&&` one `loop_resolve` per item, `Deferral` keeps the item id), an emit-all that duplicated earlier lenses on re-run (now: resumable per `(pr, head, lens)`), a fail-closed claim a token allowlist cannot make (now: stated fail-open, TOCTOU + global tokens added, the bound measured in Step 5 and carried into the spec leg), a `lens skipped` row with no emitter (now: a typed `--skipped-reason` path in the code PR), a contention test that let an every-retry emitter pass (now: exactly one row per event, cause/holder/backoff pinned), and the diagram's primary node still saying `yield` — all absorbed, each marked "codex r3 on b-230-register".
- Codex r2 (head `2a3c66b8b`) found eight more — a movable `actions/checkout@v4` tag on the job that decides whether heavy checks run, dedupe placed at the emitter instead of the banner reducer, a Bash-only `${@:4}` in an `sh -cu` recipe with a dry-run test that could not exercise it, a hard-coded ledger path bypassing `loop_status_path()` and the pending reducer, a batch that dropped failed verifications instead of aborting, a detector missing the timeout/cancellation surfaces the lens prompt names, pre-assigned spec versions that collide, and a diagram label (and the same sentence in ship-pr) saying a held lease *yields* when `wait_for_door` sleeps and retries synchronously — all absorbed, each marked "codex r2 on b-230-register".
- Codex r1 on the registration PR (b-230-register, head `02f656c72`) found eight design defects in the task bodies — clean rounds and rejected adjudications missing from the baseline, fixed positionals that could not express a valid close-out, a parser and producer disagreeing on the deferral row shape, a just recipe that stopped at a recorded BLOCK, a detector reading surviving files instead of the diff, lens gating and `--delete-branch` mis-classified as operator-only decisions, and a mid-door gate-log write that could never reach merged history — and every one is absorbed above, each marked "codex r1 on b-230-register" at the sentence it changed.
- Names used across tasks: `classify`, `build_push_command`, `parse_pending`, `Deferral`, `UnreadableRow`, `verify_all`, `VerificationMismatch`, `remote_absent`, `loop_resolve`, `resolve_cleared`, `touches_concurrency`, `EmptyDiff`, `summarize` are each defined in the task that introduces them.
