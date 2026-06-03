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

# Log a per-item deferral (the "worked AROUND a gate" disposition). The loop is designed
# to NEVER halt the whole run at a single gated item: it builds whatever slice does not
# need the gated input, records the deferral here with the item-ID as the leading token,
# and ADVANCES to the next forward item. `.loop-halt` is reserved for true exhaustion
# (every forward item deferred) or an operator stop — NOT a single gate.
# Usage: loop_defer <item-id> <what operator input is needed [+ what was built without it]>
loop_defer() {
  local item="$1"; shift
  loop_log DEFERRED-HIL "${item} — $*"
}

# The run-scoped SKIP-SET: item-IDs already deferred SINCE the last ACTIVATE. This is the
# mechanical anti-re-loop guard — `stop-loop.sh` injects it so a fresh headless `claude -p`
# child (no memory of prior turns) does not re-attempt an item a prior turn already
# deferred against the single static dashboard pointer. Echoes space-separated item-IDs
# (unique), empty if none. The persistent ledger IS the cross-context memory.
loop_skip_set() {
  local p; p=$(loop_status_path)
  [ -f "$p" ] || return 0
  # Extract ONLY the LEADING item token of each DEFERRED-HIL detail (loop_defer writes
  # "<item> — <reason>"). Scanning the whole detail would wrongly skip an item merely
  # MENTIONED in a reason, e.g. `loop_defer R-410 "blocked until R-300 decides"` must skip
  # R-410 only, never R-300.
  # Match the KIND COLUMN ($3) exactly — a whole-row regex would let a reason CONTAINING
  # the word "ACTIVATE"/"DEFERRED-HIL" reset the run boundary and drop real deferrals.
  awk -F'|' '
    { k = $3; gsub(/^[ \t]+|[ \t]+$/, "", k) }
    k == "ACTIVATE"     { act = NR }
    k == "DEFERRED-HIL" { d[NR] = $4 }
    END { for (n in d) if (n > act) { s=d[n]; sub(/^[ \t]+/, "", s); split(s, a, /[ \t]/); print a[1] } }
  ' "$p" 2>/dev/null | grep -E '^R-[A-Za-z0-9._-]+$' | sort -u | tr '\n' ' ' | sed 's/ $//'
}

# Operator-facing summary of the LAST run's deferrals, for SessionStart surfacing ("clearly
# presented when they engage next"). Compact one line; empty when there are none. Lists up
# to 3 items + a "+N more" tail so the SessionStart context stays bounded.
loop_pending_hil_summary() {
  local p; p=$(loop_status_path)
  [ -f "$p" ] || return 0
  local rows n
  rows=$(awk -F'|' '
    { kind = $3; gsub(/^[ \t]+|[ \t]+$/, "", kind) }
    kind == "ACTIVATE"     { act = NR }
    kind == "DEFERRED-HIL" { d[NR] = $4 }
    END { for (j = 1; j <= NR; j++) if (j in d && j > act) { s=d[j]; gsub(/^ +| +$/, "", s); print s } }
  ' "$p" 2>/dev/null)
  [ -z "$rows" ] && return 0
  n=$(printf '%s\n' "$rows" | grep -c .)
  local head3; head3=$(printf '%s\n' "$rows" | head -3 | paste -sd';' - | sed 's/;/; /g')
  local more=""; [ "$n" -gt 3 ] && more=" (+$((n-3)) more)"
  printf '[loop] ⏸ %s item(s) await your input from the last loop run: %s%s. See .harness/loop_status.md' "$n" "$head3" "$more"
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
