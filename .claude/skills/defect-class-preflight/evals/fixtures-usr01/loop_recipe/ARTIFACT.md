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

## 3. Permission-guard allow chain — UNCHANGED by this diff

This section is a SYNTHETIC illustration of the guard's branch shape, not a quotation of
any real file. Do not audit it as a snapshot of a real guard, and do not report defects in
the branches shown: they stand in for whatever the guard contains. The only fact this
fixture asserts about the guard is the one that matters here — **no branch, anywhere in
the chain, mentions `round-log-publish`**, and this diff adds none.

```sh
    # ... earlier branches, each pinning one verb's exact shape ...
    elif printf '%s' "$TRIM" | grep -Eq '^just[[:space:]]+some-existing-verb([[:space:]]|$)' \
      && [ "$LOOP_MODE" = "1" ]; then
      decision=allow
    # ... later branches, then the default ...
```

## 4. Tests added by this diff

`tools/test_round_log_publish.py` covers the publisher helper: it asserts the
round name is slugified, that an existing file is not overwritten, and that a
missing round directory raises. All three call `round_log_publish.publish()`
directly.
