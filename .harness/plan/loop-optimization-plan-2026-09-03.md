# Code Implementation Loop Optimization Plan

> **For agentic workers:** each task is one arc through this workspace's loop: `roadmap-continue` picks it from the forward-register row Task 9 creates, the arc lands through `ship-pr` (Codex round, CI, merge-gate for code-touching diffs, door, refresh). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut the wall-clock and token cost of one landed unit (continue → refresh merge) without weakening any gate that has caught a real defect.

**Architecture:** Six cost categories were surfaced by the Archify diagrams at `docs/diagrams/code-loop/`. Grounding on 2026-09-03 sorted them into workspace-ops changes (CI workflow, hooks, just recipes, skill procedure) that land as ordinary PRs, and spec-governed changes (C-HE-06 / C-HE-07 in `.harness/spec/Spec_HE_Loop_Lanes_v1.md`, cleared v1.7 on 2026-09-02) that need a spec leg plus a clearance marker before any code moves. Tasks are ordered by measured value over cost. Every task carries the witness that proves its saving against the baseline in §0.

**Tech Stack:** GitHub Actions (`.github/workflows/ci.yml`), bash hooks under `tools/hooks/`, `justfile` recipes, Python 3.12 tools under `tools/`, the merge-gate and ship-pr skills under `.claude/skills/`.

## Global Constraints

- Posture is mode-agnostic for Tasks 1–6 (they touch `.github/`, `tools/`, `justfile`, `.claude/skills/`). Tasks 7–8 edit `.harness/spec/Spec_HE_Loop_Lanes_v1.md` and need a version bump, a change note, a clearance marker under `.harness/clearance/`, and the HE plan update, before their code lands.
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
| Unique catches by lens | witness-adequacy 22, spec-conformance 10, concurrency 1 (of 88 concurrency findings) | script in Task 0 |
| Per-call hook cost | `post-merge-refresh.sh:45`, `precmd-clear-cache.sh:28`, `rtk-shape-guard.sh:69` exit within one grep of an ordinary Bash call; `permission-guard.sh:67` exits unless loop mode | grounding |
| Prompt hook signal | `[roadmap] next=?` on every prompt this session (`prompt-context.sh:57` prints `?` when `hook_roadmap_next` returns empty, `tools/hooks/lib.sh:267-286`) | observed |
| Branch-hygiene deferrals waiting on the operator | 3 plus one TTL re-surface in the session banner | observed |

The hooks category collapses to two defects (the empty `next=` token and duplicated banner lines); the per-call hooks are already cheap. The serialization category collapses to lease *duration* until Task 8 Step 1 makes in-budget contention measurable; only two hour-long stalls are on record in 65 arcs.

---

### Task 0: Baseline script

**Files:**
- Create: `tools/loop_cost_baseline.py`
- Test: `tools/test_loop_cost_baseline.py`

**Interfaces:**
- Produces: `python tools/loop_cost_baseline.py [--log PATH]` printing a JSON object with keys `rows`, `arcs`, `rounds_per_arc_median`, `gate_rounds_with_findings`, `single_lens_rounds`, `unique_catch_by_producer`, `lease_acquire_events`.

- [ ] **Step 1: Write the failing test**

```python
# tools/test_loop_cost_baseline.py
import json, subprocess, sys, pathlib

def test_baseline_reports_expected_keys(tmp_path):
    log = tmp_path / "log.jsonl"
    rows = [
        {"record_kind": "finding", "arc_id": "a", "round_n": 1, "producer": "codex_review_wrapper", "unique_catch": False},
        {"record_kind": "finding", "arc_id": "a", "round_n": 2, "producer": "merge-gate-witness-adequacy", "unique_catch": True},
        {"record_kind": "HITL-recoverable", "arc_id": "a", "round_n": 2, "producer": "merge-door-lease-acquire"},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    out = subprocess.run([sys.executable, "tools/loop_cost_baseline.py", "--log", str(log)], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    assert data["rows"] == 3
    assert data["arcs"] == 1
    assert data["gate_rounds_with_findings"] == 1
    assert data["single_lens_rounds"] == 1
    assert data["unique_catch_by_producer"] == {"merge-gate-witness-adequacy": 1}
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
"""
from __future__ import annotations
import argparse, collections, json, statistics, sys
from pathlib import Path

def summarize(rows: list[dict]) -> dict:
    by_round: dict[tuple, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        if r.get("record_kind") == "finding":
            by_round[(r.get("arc_id"), r.get("round_n"))][r.get("producer")] += 1
    is_lens = lambda p: isinstance(p, str) and p.startswith("merge-gate")
    gate_rounds = [k for k, c in by_round.items() if any(is_lens(p) for p in c)]
    single = [k for k in gate_rounds if sum(1 for p in by_round[k] if is_lens(p)) == 1]
    per_arc: dict[str, set] = collections.defaultdict(set)
    for arc, n in by_round:
        per_arc[arc].add(n)
    uc = collections.Counter(r.get("producer") for r in rows if r.get("record_kind") == "finding" and r.get("unique_catch") is True)
    return {
        "rows": len(rows),
        "arcs": len(per_arc),
        "rounds_per_arc_median": statistics.median(len(v) for v in per_arc.values()) if per_arc else 0,
        "gate_rounds_with_findings": len(gate_rounds),
        "single_lens_rounds": len(single),
        "unique_catch_by_producer": dict(uc),
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
Expected: PASS; real-log output matches the §0 rows (48 gate rounds, 33 single-lens, 2 lease events).

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
import subprocess, sys, pytest
from ci_bookkeeping_diff import classify  # tools/ is the pytest rootdir; sibling modules import bare, as tools/test_arc_cost.py does

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
      - uses: actions/checkout@v4
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
- Modify: the emitter of the "a .codex-worktrees/ lane is present" line (find with `rg -n "codex-worktrees/ lane is present" tools/`)
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
**Current next action (post-#1497).** U-HE-36 landed as the R3 eval arc; the door owes its refresh, then U-HE-37 opens.
EOF
[ "$(hook_roadmap_next "$tmp")" = "U-HE-37" ] || { echo "FAIL: unquoted then-tail"; exit 1; }
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
[ -n "$(hook_roadmap_next .harness/roadmap_status.md)" ] || { echo "FAIL: live file still empty"; exit 1; }
echo "ok"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash tools/hooks/test_lib_roadmap_next.sh`
Expected: `FAIL: unquoted then-tail`.

- [ ] **Step 3: Extend the parser**

In `hook_roadmap_next` (`tools/hooks/lib.sh:267-286`) insert two rules before the existing backticked-token rules, so precedence is: plan pointer, then the token after the last `then `, then the existing quoted rules:

```bash
  # Rule 0: a backticked plan pointer wins → plan:<name>
  local plan
  plan=$(printf '%s\n' "$section" | grep -oE '`\.harness/plan/[A-Za-z0-9_.-]+\.md`' | head -1 | sed -E 's#`\.harness/plan/(.*)\.md`#plan:\1#')
  [ -n "$plan" ] && { printf '%s\n' "$plan"; return 0; }
  # Rule 1: the unit after the LAST "then " (the ship-pr "then <next unit>" tail), quoted or not
  local tail
  tail=$(printf '%s\n' "$section" | grep -oE 'then `?[UR]-[A-Z]+-[0-9]+`?' | tail -1 | grep -oE '[UR]-[A-Z]+-[0-9]+')
  [ -n "$tail" ] && { printf '%s\n' "$tail"; return 0; }
```

- [ ] **Step 4: Run the test**

Run: `bash tools/hooks/test_lib_roadmap_next.sh`
Expected: `ok`, and a fresh prompt in a new session shows `[roadmap] next=U-HE-37` (or the plan pointer once Task 9 installs it).

- [ ] **Step 5: Deduplicate the banner line**

Locate the emitter (`rg -n "codex-worktrees/ lane is present" tools/`). Wrap its output collection in `sort -u` before emission so one lane prints once per session. Witness: start a new session with a `.codex-worktrees/` lane present and count the line in the banner: expected 1.

- [ ] **Step 6: Commit**

```bash
git add tools/hooks/lib.sh tools/hooks/test_lib_roadmap_next.sh <emitter file>
git commit -m "fix(hooks): prompt-context next= recognizes plan pointers; dedupe worktree lane notice"
```

---

### Task 3: One-invocation arc close-out (serial tail)

The close-out after the door releases is eight serial steps (`.claude/skills/ship-pr/SKILL.md:387-644`). Reflect and `/context-save-lean` need the session; the exit report, metrics queue, and deferral rows do not. Fold those three into one recipe.

**Files:**
- Modify: `justfile` (add `arc-close` next to `arc-exit-report` at line 265)
- Modify: `.claude/skills/ship-pr/SKILL.md:541-624` (replace the two separate invocations with `just arc-close`)
- Test: `tools/test_arc_close_recipe.py`

- [ ] **Step 1: Write the failing test**

```python
# tools/test_arc_close_recipe.py
import subprocess

def test_arc_close_recipe_exists():
    out = subprocess.run(["just", "--list"], capture_output=True, text=True, check=True).stdout
    assert "arc-close" in out
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tools/test_arc_close_recipe.py -v`
Expected: FAIL.

- [ ] **Step 3: Add the recipe**

```just
# Loop optimization plan Task 3: the non-interactive close-out tail in one call.
# Runs exit-report then metrics queue; just runs each line in its own shell and stops at the first non-zero exit.
arc-close pr merge_sha checkpoint arc_id arc_type decisions round_logs transcript levers:
    just arc-exit-report --pr {{pr}} --merge-sha {{merge_sha}} --checkpoint {{checkpoint}}
    just arc-metrics queue --pr {{pr}} --arc-id {{arc_id}} --arc-type {{arc_type}} --decisions {{decisions}} --round-logs '{{round_logs}}' --transcript {{transcript}} --levers {{levers}}
```

- [ ] **Step 4: Run the test, then a dry run**

Run: `uv run pytest tools/test_arc_close_recipe.py -v && just --show arc-close`
Expected: PASS; recipe body printed.

- [ ] **Step 5: Update ship-pr**

In `.claude/skills/ship-pr/SKILL.md` §"Arc exit report" and §"Arc-metrics capture", replace the two command blocks with the single `just arc-close ...` invocation and keep the surrounding rules (skip when the PR was itself the refresh; queue writes outside the repo). Run `just codex-check` (the docs and citation gates read skill files).

- [ ] **Step 6: Commit**

```bash
git add justfile .claude/skills/ship-pr/SKILL.md tools/test_arc_close_recipe.py tools/codex-parity-check.sh
git commit -m "feat(just): arc-close folds exit-report + metrics queue into one close-out call"
```

Leave the cross-arc metrics drain as it is. Its reason is durability (`ship-pr/SKILL.md:604-611`, `justfile:232-234`): a row is released only once it is in merged history, and a topic worktree must never be left dirty. That is a correct constraint, not waste.

---

### Task 4: Batched branch hygiene (one approval instead of N)

**Files:**
- Create: `tools/branch_hygiene_batch.py`
- Modify: `justfile` (add `branch-hygiene-pending`)
- Modify: `.claude/skills/ship-pr/SKILL.md:471-480` (point the deferral text at the batch recipe)
- Test: `tools/test_branch_hygiene_batch.py`

**Interfaces:**
- Produces: `python tools/branch_hygiene_batch.py --pending <loop_status.md>` prints one line per verified-merged branch as `<branch> <head_oid>` and, with `--emit-command`, prints the single guarded push:
  `git push --force-with-lease=refs/heads/A:<oidA> --force-with-lease=refs/heads/B:<oidB> origin :refs/heads/A :refs/heads/B`

- [ ] **Step 1: Write the failing test**

```python
# tools/test_branch_hygiene_batch.py
from branch_hygiene_batch import build_push_command  # tools/ is the pytest rootdir; sibling modules import bare, as tools/test_arc_cost.py does

def test_two_branches_one_command():
    cmd = build_push_command([("feat/a", "aaa111"), ("roadmap-refresh-post-1", "bbb222")])
    assert cmd == ("git push --force-with-lease=refs/heads/feat/a:aaa111 "
                   "--force-with-lease=refs/heads/roadmap-refresh-post-1:bbb222 "
                   "origin :refs/heads/feat/a :refs/heads/roadmap-refresh-post-1")

def test_empty_list_is_an_error():
    import pytest
    with pytest.raises(ValueError):
        build_push_command([])

def test_parse_pending_row_finds_both_branches():
    from branch_hygiene_batch import parse_pending
    row = ("u-sr-08 — branch hygiene close-out pending: feat/u-sr-08-context-noise-deletions "
           "(PR #1489, merged 9032fead4, main run green) and roadmap-refresh-post-1489 "
           "(PR #1490, merged ff62189d2, main run green) — run the guarded force-with-lease delete block")
    assert parse_pending(row) == [("feat/u-sr-08-context-noise-deletions", "1489"), ("roadmap-refresh-post-1489", "1490")]
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
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys

PENDING = re.compile(r"branch hygiene close-out pending: (?P<rest>.*)")
BRANCH = re.compile(r"(?P<branch>[\w./-]+) \(PR #(?P<pr>\d+), merged")

def parse_pending(text: str) -> list[tuple[str, str]]:
    """Every '<branch> (PR #N, merged' pair inside each pending row: the content branch AND its refresh branch."""
    out: list[tuple[str, str]] = []
    for m in PENDING.finditer(text):
        out.extend((b.group("branch"), b.group("pr")) for b in BRANCH.finditer(m.group("rest")))
    return out

def build_push_command(branches: list[tuple[str, str]]) -> str:
    if not branches:
        raise ValueError("no verified branches to delete")
    leases = " ".join(f"--force-with-lease=refs/heads/{b}:{oid}" for b, oid in branches)
    refs = " ".join(f":refs/heads/{b}" for b, _ in branches)
    return f"git push {leases} origin {refs}"

def verified(branch: str, pr: str) -> tuple[str, str] | None:
    info = json.loads(subprocess.run(["gh", "pr", "view", pr, "--json", "state,headRefName,headRefOid"], capture_output=True, text=True, check=True).stdout)
    if info["state"] != "MERGED" or info["headRefName"] != branch:
        return None
    return (branch, info["headRefOid"])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending", required=True)
    ap.add_argument("--emit-command", action="store_true")
    a = ap.parse_args()
    found = parse_pending(open(a.pending).read())
    ok = [v for v in (verified(b, pr) for b, pr in found) if v]
    for b, oid in ok:
        print(f"{b} {oid}")
    if a.emit_command:
        print(build_push_command(ok))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test**

Run: `uv run pytest tools/test_branch_hygiene_batch.py -v`
Expected: 3 passed.

- [ ] **Step 5: Recipe and skill text**

```just
# Task 4: list verified-merged deferred branches and print the ONE guarded delete to run by hand.
branch-hygiene-pending:
    uv run python tools/branch_hygiene_batch.py --pending "$HOME/.gstack/projects/arhugula-v2/loop_status.md" --emit-command
```

In `ship-pr/SKILL.md:471-480`, after the `defer.sh` sentence, add: "In the next interactive session run `just branch-hygiene-pending` and paste the printed push; one approval clears every verified row."

- [ ] **Step 6: Witness and commit**

Run `just branch-hygiene-pending` against the current three deferrals; expected: six `branch oid` lines (each row names a content branch and its refresh branch) and one push command. Do not run the push inside this task's PR; the operator runs it. Then:

```bash
git add tools/branch_hygiene_batch.py tools/test_branch_hygiene_batch.py justfile .claude/skills/ship-pr/SKILL.md tools/codex-parity-check.sh
git commit -m "feat(tools): branch_hygiene_batch — one guarded push for all deferred deletions"
```

---

### Task 5: Merge-gate emit in one call (smaller items)

Today the gate publishes three bindings, then emits three verdicts, each as its own `just` call (`merge-gate/SKILL.md:74-87,171-195`).

**Files:**
- Modify: `justfile` recipes `merge-gate-binding` (line 351) and `merge-gate-emit` (line 359): add `merge-gate-emit-all` that takes the three verdict files.
- Modify: `.claude/skills/merge-gate/SKILL.md:171-195` to call it.
- Test: `tools/test_merge_gate_emit_all.py`, asserting the recipe forwards to the existing emitter three times with the fixed lens order and stops at the first non-zero exit.

- [ ] **Step 1: Write the failing test** (recipe presence and body, same shape as Task 3 Step 1, plus `just --show merge-gate-emit-all` containing the three lens ids in order `merge-gate-concurrency`, `merge-gate-spec-conformance`, `merge-gate-witness-adequacy`).
- [ ] **Step 2: Run it, expect FAIL.**
- [ ] **Step 3: Add the recipe**

```just
merge-gate-emit-all pr arc_id concurrency_json spec_json witness_json:
    just merge-gate-emit --pr {{pr}} --arc-id {{arc_id}} --lens merge-gate-concurrency --verdict-json {{concurrency_json}}
    just merge-gate-emit --pr {{pr}} --arc-id {{arc_id}} --lens merge-gate-spec-conformance --verdict-json {{spec_json}}
    just merge-gate-emit --pr {{pr}} --arc-id {{arc_id}} --lens merge-gate-witness-adequacy --verdict-json {{witness_json}}
```

- [ ] **Step 4: Run the test, expect PASS.**
- [ ] **Step 5: Update the skill text and commit** with `git commit -m "feat(just): merge-gate-emit-all"`.

The second disjointness check at ship time stays: HEAD changed since selection, so it is not a duplicate.

---

### Task 6: Concurrency lens on demand (duplicate reviews, decision-gated)

Basis: the concurrency lens has 1 unique catch in 88 findings; witness-adequacy has 22 and spec-conformance 10. Running the concurrency lens only when the diff touches a shared-state or process-isolation surface removes one subagent from the gate rounds the detector clears; Step 5 measures how many that is. This changes what "all three APPROVE" means for a round where the lens did not run, so it is an operator decision. Build the detector first, then ask once.

**Files:**
- Create: `tools/concurrency_surface.py`
- Test: `tools/test_concurrency_surface.py`
- Modify (after the decision): `.claude/skills/merge-gate/SKILL.md:110-169` and `:197-219`.

- [ ] **Step 1: Write the failing test**

```python
# tools/test_concurrency_surface.py
from concurrency_surface import touches_concurrency  # tools/ is the pytest rootdir; sibling modules import bare, as tools/test_arc_cost.py does

def test_asyncio_file_is_a_surface(tmp_path):
    f = tmp_path / "a.py"; f.write_text("import asyncio\nlock = asyncio.Lock()\n")
    assert touches_concurrency([f]) is True

def test_plain_async_def_is_not_a_surface(tmp_path):
    f = tmp_path / "d.py"; f.write_text("import asyncio\nasync def x(): await y()\n")
    assert touches_concurrency([f]) is False

def test_plain_file_is_not(tmp_path):
    f = tmp_path / "b.py"; f.write_text("def y(): return 1\n")
    assert touches_concurrency([f]) is False

def test_lock_file_is_a_surface(tmp_path):
    f = tmp_path / "c.py"; f.write_text("import fcntl\n")
    assert touches_concurrency([f]) is True
```

- [ ] **Step 2: Run it, expect FAIL.**
- [ ] **Step 3: Write the detector**

```python
#!/usr/bin/env python3
"""Does a changed-file set touch a concurrency surface? (Task 6 of the loop optimization plan.)"""
from __future__ import annotations
import re, sys
from pathlib import Path

PATTERN = re.compile(r"\b(asyncio\.(gather|create_task|Lock|Semaphore|Queue)|threading|multiprocessing|concurrent\.futures|fcntl|os\.link|O_EXCL|subprocess\.Popen|Lock\(|Semaphore\()")
# Deliberately not `await ` or bare `asyncio`: nearly every harness diff is async; the lens is for shared-state and process-isolation surfaces.

def touches_concurrency(paths: list[Path]) -> bool:
    return any(p.suffix == ".py" and PATTERN.search(p.read_text(errors="ignore")) for p in paths)

if __name__ == "__main__":
    print("concurrency=" + ("true" if touches_concurrency([Path(p) for p in sys.argv[1:]]) else "false"))
```

- [ ] **Step 4: Run the test, expect PASS. Commit** `git commit -m "feat(tools): concurrency_surface detector (merge-gate lens gating, decision pending)"`.
- [ ] **Step 5: Measure on history** — for the last 20 gate rounds, run the detector on each PR's changed files and record how many rounds would have skipped the lens and whether any of the lens's 88 findings (the 1 unique catch above all) would have been lost. Put the table in this plan under §0.
- [ ] **Step 6: One AskUserQuestion** with the table: (a) run the concurrency lens only when the detector says `true`, recording `lens skipped: no concurrency surface` as a `no_finding` row so C-HE-29 accounting stays whole; (b) keep three lenses always. Apply the skill edit only on (a).

The Codex re-run after a lens BLOCK stays. A fix is new code and the out-of-family reviewer has never seen it; the log shows 2039 Codex rows for 343 lens rows, so the re-run is where the catches are.

---

### Task 7: Spec leg — `--delete-branch` in the fixed merge string (optional, policy change)

Deleting the topic branch inside the door removes the deferral queue Task 4 batches. It conflicts with the standing rule that branch deletion is a per-instance human decision (`ship-pr/SKILL.md:471-480`). Offer it; do not build it unless the operator changes the rule.

**Files (only after the decision):**
- Modify: `.harness/spec/Spec_HE_Loop_Lanes_v1.md:294` (C-HE-06 §4 iv) and `:334-338` (C-HE-07 §1), bump to v1.8 with a change note.
- Create: `.harness/clearance/spec-he-loop-lanes-v1.8-cleared-<date>.md`
- Modify: `tools/merge_door.py:896`, `tools/hooks/safe-merge.sh:2-4`, `tools/hooks/permission-guard.sh` allowlist, `tools/hooks/test_permission_guard.sh:174,279` (the two denied `--delete-branch` cases flip to allowed for the door's exact shape only), `.harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md`.

- [ ] **Step 1:** Present the decision in the same AskUserQuestion as Task 6 Step 6, recommending **no** for now: Task 4 already collapses the cost to one approval per session, and the rule exists because deletion is irreversible.
- [ ] **Step 2 (only on yes):** file the spec change note, land the spec + marker PR first (doc-only, no code, so the context guard's DESIGN_IMPL_MIX rule stays clean), then land the code PR with the four file edits and the two flipped guard tests.

---

### Task 8: Spec leg — lease scope and N-merge refresh (deferred, trigger-gated)

Releasing the lease after the content merge and letting one refresh cover N merges would end serialization, but it needs three coupled changes: C-HE-06 invariants (`Spec_HE_Loop_Lanes_v1.md:317-321`), the §12.2.1 one-commit fixed point in root `CLAUDE.md`, and `_owed_lag` in `tools/codex_context_guard.py:443-469`. The data cannot justify it yet, in either direction: the only `merge-door-lease-acquire` row the door writes is the budget-exhausted one (`tools/merge_door.py:1965`, `lease_acquire_budget_exhausted`, after twelve backoffs of up to ten minutes). A yield that resolves inside the budget writes nothing, so "2 rows in 65 arcs" counts hour-long stalls, not contention. Task 1 cuts the hold from about 23 minutes to about 10 regardless.

- [ ] **Step 1: Make contention visible.** In `tools/merge_door.py`, at the point where `wait_for_door` first observes `held` (the caller-side backoff near `:1714`), emit one row with producer `merge-door-lease-acquire`, `record_kind: no_finding`, `finding_type: transient-retry`, `cause_attribution: lease_held_yield`, and the holder's arc id in `observed_evidence`. This adds a log row; it does not touch acquire, release, or the invariants at `Spec_HE_Loop_Lanes_v1.md:317-321`. Test: `tools/test_merge_door.py` gains one case asserting the row is written when acquire returns `held`.
- [ ] **Step 2:** Register a forward-register row (the id after Task 9's umbrella, `B-231` if nothing else lands first) titled "Merge-door lease released after content merge; refresh covers N merges", with the trigger "more than 5 `lease_held_yield` rows in any 30-day window after Task 1 lands" and the three cites above.
- [ ] **Step 3:** Re-run `tools/loop_cost_baseline.py` at each roadmap refresh (extend it to count `lease_held_yield`); when the trigger fires, open the spec leg as a Class 2 decision with a proposed v1.9 text.

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
    the plan §0, Task 6 and Task 7 have an operator answer, and Task 8 Step 1 (yield
    row) is merged so its trigger is measurable.'
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
| 7 | Task 6 lens gating | decision | one subagent fewer in the gate rounds the detector clears (Step 5 measures how many) | changes the gate's basis; ask once with data |
| 8 | Task 7 delete-branch | spec leg, policy | removes the deferral queue | irreversible deletion moves into the door; recommend no |
| 9 | Task 8 lease scope | spec leg, trigger-gated | ends serialization | contention is unmeasured until Step 1 lands; two hour-long stalls on record |

Each task is its own PR and its own arc through the loop it optimizes. Re-run `uv run python tools/loop_cost_baseline.py` and `gh run view <latest main run> --json jobs` after each merge and append the numbers to §0.

## Self-review

- Registration: Task 9 first, so the loop derives the next task instead of parking the plan.
- Coverage: CI runs → Task 1; serialization → Task 1 (duration) + Task 8 (trigger); duplicate reviews → Task 6 (gated) with the Codex re-run kept; hooks → Task 2 (the two real defects); close-out tail and cross-arc coupling → Task 3 (tail) with the coupling left in place for a stated reason; smaller items → Tasks 4 and 5, disjointness check kept.
- No task edits the fixed merge string, releases the lease early, or drops the CI-at-final-head rule without a spec leg.
- Names used across tasks: `classify`, `build_push_command`, `parse_pending`, `touches_concurrency`, `summarize` are each defined in the task that introduces them.
