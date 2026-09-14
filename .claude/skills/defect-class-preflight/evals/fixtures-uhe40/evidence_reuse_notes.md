# Pre-commit notes — reuse recorded probe ranges and replay results

## What changed

Two caches, both to avoid repeating slow work:

1. `tools/checks/reverify.py` looks up the latest row in `.harness/probe-log.jsonl` for an
   annotation and re-runs that row's `lines` range against the annotated file:

   ```python
   row = latest_row(log, node=node, file=target)
   rc = probe(target, row["lines"], node)   # row also records target_sha / test_sha
   ```

2. `tools/checks/replay.py` measures a check over the last 20 merged arcs and skips any arc that
   already has rows on the gate log for that check:

   ```python
   arc_id = f"replay-{sha[:12]}"
   measured = {r["arc_id"] for r in rows if r["producer"] == check.check_id}
   todo = [s for s in shas if f"replay-{s[:12]}" not in measured]
   ```

   Promotion to blocking evaluates the adjudicated rows of those 20 arc ids.

## Tests

`test_reverify_uses_logged_range` and `test_replay_skips_measured_arcs` (a second replay runs
nothing).
