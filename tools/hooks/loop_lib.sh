#!/usr/bin/env bash
# Loop-mode ledger library (U-HK-11) — the Wave-2 autonomy substrate.
#
# Sourced by the Wave-2 autonomy hooks (permission-guard, stop-loop, resolve) and
# the /loop-start | /loop-stop skills. Provides the loop-mode marker toggle and an
# append-only status ledger at .harness/loop_status.md that records the things a
# human will want to review after an unattended run: deferred genuinely-blocking
# HILs (creds / vendor / paid calls), what the loop completed AROUND them, hard-stop
# denials, Codex+Advisor decision splits, and resume state.
#
# Depends on lib.sh (hook_project_dir, loop_mode_active). Source lib.sh FIRST, then
# this. Pure library — no `set -e` (would surprise the sourcing script). The only
# side-effects are the explicit file ops in loop_activate / loop_deactivate / loop_log.
# Test with tools/hooks/test_loop_lib.sh.

# Path to the loop-mode marker file (presence === loop active, alongside HARNESS_LOOP=1).
# Echoes empty if the project dir cannot be resolved (caller should treat as off).
loop_marker_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/.loop-active"
}

# Path to the append-only status ledger.
loop_status_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/loop_status.md"
}

# Path to the Stop-continue iteration counter (U-HK-14 bound). Presence + integer
# value cap the number of auto-continued turns per run.
loop_iter_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/.loop-iter"
}

# Path to the halt marker (U-HK-14). When present, the next Stop stops the loop — the
# explicit "we hit a genuine gate, stand down" signal Claude/skills drop at a gate.
loop_halt_path() {
  local d; d=$(hook_project_dir)
  [ -n "$d" ] && printf '%s' "$d/.harness/.loop-halt"
}

# A UTC ISO-8601 timestamp (second precision). Isolated so tests can stub it.
loop_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Ensure the ledger exists, creating it from the canonical header if absent.
# Idempotent. Echoes the path (empty if unresolvable).
loop_status_ensure() {
  local p; p=$(loop_status_path)
  [ -z "$p" ] && return 0
  if [ ! -f "$p" ]; then
    mkdir -p "$(dirname "$p")" 2>/dev/null
    cat > "$p" <<'EOF'
# Loop status ledger

*Append-only record of autonomous loop-mode activity (Wave 2, U-HK-11). OFF by
default — rows are written only while loop mode is active (`HARNESS_LOOP=1` or the
`.harness/.loop-active` marker). Review after an unattended run: each `DEFERRED-HIL`
is a genuine gate (creds / vendor / paid call / destructive op) the loop refused to
auto-fire and worked around; `DENY` is a hard-stop the permission guard blocked;
`RESOLVE-SPLIT` is a Codex+Advisor disagreement where the safer default was taken.*

| timestamp | kind | detail |
|---|---|---|
EOF
  fi
  printf '%s' "$p"
}

# Append a ledger row. Usage: loop_log <kind> <detail...>
# kind is a short uppercase token (ACTIVATE / DEACTIVATE / DEFERRED-HIL / COMPLETED /
# DENY / RESOLVE-SPLIT / RESUME). detail is free text (pipes are escaped so the
# markdown table stays well-formed). Always exits 0 (a ledger write must never break
# the calling hook). No-op if the project dir cannot be resolved.
loop_log() {
  local kind="$1"; shift
  local detail="$*"
  local p; p=$(loop_status_ensure)
  [ -z "$p" ] && return 0
  # Escape pipes + collapse newlines so one logical row stays one table row.
  detail=$(printf '%s' "$detail" | tr '\n' ' ' | sed 's/|/\\|/g')
  printf '| %s | %s | %s |\n' "$(loop_now)" "$kind" "$detail" >> "$p" 2>/dev/null || true
}

# Turn loop mode ON: create the marker + log the activation. Usage: loop_activate [reason]
loop_activate() {
  local mp; mp=$(loop_marker_path)
  [ -z "$mp" ] && return 1
  mkdir -p "$(dirname "$mp")" 2>/dev/null
  : > "$mp" 2>/dev/null || return 1
  # Fresh run: clear any stale iteration counter / halt marker from a prior run.
  rm -f "$(loop_iter_path)" "$(loop_halt_path)" 2>/dev/null
  loop_log ACTIVATE "${1:-loop mode on}"
}

# Turn loop mode OFF: remove the marker + log the deactivation. Usage: loop_deactivate [reason]
# Note: HARNESS_LOOP=1 in the environment still forces loop mode on even after this
# (env wins); deactivate clears the file marker only.
loop_deactivate() {
  local mp; mp=$(loop_marker_path)
  [ -z "$mp" ] && return 1
  rm -f "$mp" "$(loop_iter_path)" "$(loop_halt_path)" 2>/dev/null
  loop_log DEACTIVATE "${1:-loop mode off}"
}
