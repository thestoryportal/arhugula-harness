---
name: loop-stop
description: Turn OFF autonomous loop mode for the harness workspace (Wave 2 U-HK-11). Use when the operator says "/loop-stop", "stop the loop", "end autonomous mode", "go back to interactive", or wants to disable the guardrailed auto-approve / auto-continue tier. Removes the .harness/.loop-active marker so the Wave-2 autonomy hooks (auto-approve U-HK-12, Stop-continue U-HK-14) go inert again.
---

# loop-stop — disable autonomous loop mode

Returns the workspace to normal interactive operation. The Wave-2 autonomy hooks go
inert; every tool call returns to manual approval and turns end normally.

## Run

```bash
source tools/hooks/lib.sh && source tools/hooks/loop_lib.sh && loop_deactivate "operator /loop-stop"
echo "loop mode: $(loop_mode_active && echo ON || echo OFF)"
```

## Notes

- Removes the `.harness/.loop-active` file marker and logs a `DEACTIVATE` row.
- **`HARNESS_LOOP=1` in the environment overrides the marker** — if loop mode still
  reports ON after this, an env var is forcing it; unset `HARNESS_LOOP` to fully disable.
- Review `.harness/loop_status.md` for what the run deferred (`DEFERRED-HIL` rows are
  the genuine gates — creds / paid calls / destructive ops — that need your attention).
