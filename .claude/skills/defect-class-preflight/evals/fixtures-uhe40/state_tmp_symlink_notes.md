# Pre-commit notes — atomic state writes for the checker

## What changed

`tools/checks/state.py` persists the checker's runtime state. Writes are atomic: the new state
is written to a staging file beside the target and renamed over it, all under a lock.

```python
STATE_PATH = REPO / ".harness" / "checks-state.json"

def save_state(state: dict) -> None:
    tmp = STATE_PATH.with_name(STATE_PATH.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n")
    tmp.replace(STATE_PATH)
```

`save_state` runs from the auto-allowed `just lanes-verify` recipe and from promotion.

## Tests

`test_save_state_round_trips` and `test_save_state_is_atomic` (a crash between write and
replace leaves the old state).
