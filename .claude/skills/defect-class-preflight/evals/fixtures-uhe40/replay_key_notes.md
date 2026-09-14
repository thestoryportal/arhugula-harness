# Pre-commit notes — measure each replayed arc once

## What changed

`tools/checks/runner.py` replays a check over the last 20 merged arcs. Measuring an arc is slow (a
detached worktree per arc), so results are reused: an arc already measured by the same checker
implementation is skipped.

```python
impl = implementation_digest()  # sha256 over tools/**/*.py
arc_ids = [f"replay-{sha[:12]}-{impl}" for sha in shas]
measured = {r["arc_id"] for r in read_rows() if r["producer"] == check.check_id}
for sha, arc_id in zip(shas, arc_ids):
    if arc_id in measured:
        continue
    with commit_subject(repo, sha, pr_body=gh_pr_body) as subject:  # fetches `gh pr view N`
        emit(check.check_id, check.run(subject), arc_id=arc_id)
```

`commit_subject` fills `Subject.pr_body` from `gh pr view` (None when gh fails). The `unrun_cli`
check reads claims from the PR body and reports an info finding when it is None.

## Tests

`test_replay_measures_each_arc_once` (a second replay runs no check) and
`test_changed_implementation_remeasures` (a new digest re-measures every arc).
