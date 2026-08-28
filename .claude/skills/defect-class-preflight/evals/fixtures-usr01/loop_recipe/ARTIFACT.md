# Proposed change — round-log publish recipe

## 1. New `justfile` recipe

```make
# Publish this arc's round log to the shared drain.
round-log-publish ROUND:
    uv run python tools/round_log_publish.py --round {{ROUND}}
```

## 2. Verification-manifest row added for it

| Contract | Artifact | Tag | runs_in | mutation_probe | Notes |
|---|---|---|---|---|---|
| C-HE-27 | `just:round-log-publish` | phase1 | operator/loop | no | publishes the round log the metrics reader consumes |

## 3. Permission-guard allow chain (`tools/hooks/permission-guard.sh`) — UNCHANGED by this diff

The chain's tail, quoted as it stands on main:

```sh
    elif printf '%s' "$TRIM" | grep -Eq '^just[[:space:]]+review-with-failover-logged([[:space:]]|$)' \
      && [ "$LOOP_MODE" = "1" ]; then
      decision=allow
    elif printf '%s' "$TRIM" | grep -Eq '^just[[:space:]]+merge-gate-adjudicate([[:space:]]|$)' \
      && [ "$LOOP_MODE" = "1" ]; then
      decision=allow
```

## 4. Tests added by this diff

`tools/test_round_log_publish.py` covers the publisher helper: it asserts the
round name is slugified, that an existing file is not overwritten, and that a
missing round directory raises. All three call `round_log_publish.publish()`
directly.
