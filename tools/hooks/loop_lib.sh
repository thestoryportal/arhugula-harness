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
auto-fire and worked around; a later `RESOLVED-HIL` row for the same item-id clears it
once the gate is answered (ratification, operator selection, etc.); `DENY` is a
hard-stop the permission guard blocked; `RESOLVE-SPLIT` is a Codex+Advisor disagreement
where the safer default was taken.*

| timestamp | kind | detail |
|---|---|---|
EOF
  fi
  printf '%s' "$p"
}

# Append a ledger row. Usage: loop_log <kind> <detail...>
# kind is a short uppercase token (ACTIVATE / DEACTIVATE / DEFERRED-HIL / RESOLVED-HIL /
# COMPLETED / DENY / RESOLVE-SPLIT / RESUME). detail is free text (pipes are escaped so the
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

# Log that a previously-deferred item's gate was subsequently answered (ratified,
# selected, decided) OUTSIDE the append-only DEFERRED-HIL row itself — e.g. via a later
# council/dyad ratification or operator AskUserQuestion that this ledger never witnessed
# directly. Without this, loop_skip_set/loop_pending_hil_summary have no way to represent
# "resolved" and the SessionStart hook nags about an already-answered gate forever (until
# the next ACTIVATE row happens to reset the window by accident).
# Usage: loop_resolve <item-id> <how it was resolved + evidence pointer>
loop_resolve() {
  local item="$1"; shift
  loop_log RESOLVED-HIL "${item} — $*"
}

# The run-scoped SKIP-SET: item-IDs deferred SINCE the last ACTIVATE and not subsequently
# RESOLVED. This is the mechanical anti-re-loop guard — `stop-loop.sh` injects it so a
# fresh headless `claude -p` child (no memory of prior turns) does not re-attempt an item
# a prior turn already deferred against the single static dashboard pointer. Echoes
# space-separated item-IDs (unique), empty if none. The persistent ledger IS the
# cross-context memory.
loop_skip_set() {
  local p; p=$(loop_status_path)
  [ -f "$p" ] || return 0
  # Extract ONLY the LEADING item token of each DEFERRED-HIL/RESOLVED-HIL detail
  # (loop_defer/loop_resolve write "<item> — <reason>"). Scanning the whole detail would
  # wrongly match an item merely MENTIONED in a reason, e.g. `loop_defer R-410 "blocked
  # until R-300 decides"` must key on R-410 only, never R-300.
  # Match the KIND COLUMN ($3) exactly — a whole-row regex would let a reason CONTAINING
  # the word "ACTIVATE"/"DEFERRED-HIL" reset the run boundary and drop real deferrals.
  # Per-token LAST-WRITE-WINS since the last ACTIVATE: a later RESOLVED-HIL row clears a
  # prior DEFERRED-HIL for the same item; a later re-DEFERRED-HIL row re-flags it.
  awk -F'|' '
    { k = $3; gsub(/^[ \t]+|[ \t]+$/, "", k) }
    k == "ACTIVATE" { delete state }
    k == "DEFERRED-HIL" || k == "RESOLVED-HIL" {
      s = $4; sub(/^[ \t]+/, "", s); split(s, a, /[ \t]/); tok = a[1]
      state[tok] = (k == "DEFERRED-HIL") ? "PENDING" : "RESOLVED"
    }
    END { for (t in state) if (state[t] == "PENDING") print t }
  ' "$p" 2>/dev/null | grep -E '^R-[A-Za-z0-9._-]+$' | sort -u | tr '\n' ' ' | sed 's/ $//'
}

# Operator-facing summary of the LAST run's still-PENDING deferrals (a RESOLVED-HIL row
# clears an item per the same last-write-wins rule as loop_skip_set), for SessionStart
# surfacing ("clearly presented when they engage next"). Compact one line; empty when
# there are none. Lists up to 3 items + a "+N more" tail so the SessionStart context
# stays bounded. Item order among >3 pending items is not chronologically guaranteed
# (awk associative-array iteration) — acceptable for advisory summary text.
loop_pending_hil_summary() {
  local p; p=$(loop_status_path)
  [ -f "$p" ] || return 0
  local rows n
  rows=$(awk -F'|' '
    { k = $3; gsub(/^[ \t]+|[ \t]+$/, "", k) }
    k == "ACTIVATE" { delete state; delete detail }
    k == "DEFERRED-HIL" || k == "RESOLVED-HIL" {
      s = $4; sub(/^[ \t]+/, "", s); split(s, a, /[ \t]/); tok = a[1]
      if (k == "DEFERRED-HIL") { state[tok] = "PENDING"; detail[tok] = s }
      else { state[tok] = "RESOLVED" }
    }
    END { for (t in state) if (state[t] == "PENDING") print detail[t] }
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
  # NOTE: worktree GC is intentionally NOT called here. `tools/04-loop/run.sh` installs its
  # `.loop-active`-cleanup EXIT/INT/TERM trap only AFTER loop_activate returns, so a slow
  # gh/GC step here would open a pre-trap interruption window that could leave loop mode
  # armed on Ctrl-C (codex P2). GC fires from the SessionStart hook (loop-gc.sh, covering
  # headless children + live re-opens + /clear) and from the /loop-start skill (covering
  # in-session activation) — both outside the runner's pre-trap path.
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

# ── Worktree garbage collection (U-HK-26) ─────────────────────────────────────
# The autonomous loop ships PRs whose worktrees go stale after merge, and nothing
# reaps them (git-arc-guard checks commits/branches; session-end-cleanup is
# advisory-only; a hook can't remove the worktree it runs INSIDE). loop_gc_worktrees
# collects them at the next session's start, self-excluding the current worktree.
#
# WORKTREES ONLY — never `git branch -d/-D`. `git worktree remove` on a clean tree is
# REVERSIBLE (branch + commits persist; `git worktree add` re-creates it); a merged
# branch ref is ~41 harmless bytes; and the irreversible force-delete that squash-merge
# would require (`-D`, because `git branch -d` does not recognize squash-merged work)
# is left to the operator via the advisory report.

# gh-availability probe: 0 iff `gh` can list merged PRs (installed + authed + reachable).
# A single upfront probe lets the GC distinguish "gh down → do nothing (fail-safe)" from
# per-branch "this branch is genuinely unmerged", and avoids N futile queries when offline.
# Runs gh INSIDE the repo dir ($1) — `gh` infers the repo from cwd, and the hook's cwd is
# not guaranteed to be the project root (codex P2 + [[bash-cwd-reverts-to-project-root]]).
_loop_gc_gh_ok() {
  command -v gh >/dev/null 2>&1 || return 1
  ( cd "$1" 2>/dev/null || exit 1
    hook_bounded 6 gh pr list --state merged --limit 1 --json number >/dev/null 2>&1 )
}

# The exact merged head SHA for ONE branch (empty if the branch has no merged PR).
# Queried PER-BRANCH via `--head` rather than a bounded recent list, so an OLD stale
# worktree whose PR is beyond the latest N merges is still found (codex P2). headRefOid
# is the pre-squash head SHA → an exact-SHA match is both precise and squash-merge-safe.
# Args: <branch> <repo_dir>. Runs gh inside <repo_dir> so the lookup targets THIS repo,
# not the caller's cwd (codex P2). Isolated so tests can stub it.
_loop_gc_merged_oid() {
  ( cd "$2" 2>/dev/null || exit 0
    hook_bounded 6 gh pr list --state merged --head "$1" --limit 5 --json headRefOid \
      --jq '.[0].headRefOid // empty' 2>/dev/null )
}

# Ignored entries matching this REGENERABLE allowlist are safe to delete when reaping
# (`git worktree remove` deletes ignored files — verified). ANYTHING else — tracked
# changes, untracked files, OR a non-allowlisted ignored entry (.env / harness.toml /
# a stray scratch file) — counts as real local state → the worktree is skipped +
# surfaced, never silently deleted. (Codex P2, 2026-06-03: the porcelain clean-check
# omitted ignored state.) `.claude/settings.local.json` IS allowlisted on purpose: in a
# worktree it is that worktree's OWN gitignored permission cache (the operator's primary
# copy lives in the main checkout and is never touched), and a reaped worktree is merged
# /done, so its cache has no forward value — unlike .env/harness.toml. Keep roughly in
# sync with the regenerable section of .gitignore.
_LOOP_GC_REGEN_IGNORED='^!! (.*/)?(\.harness/|__pycache__/|.*\.py[co]|.*\.egg-info/|\.pytest_cache/|\.ruff_cache/|\.pyright/|\.mypy_cache/|\.venv/|venv/|env/|dist/|build/|htmlcov/|coverage\.xml|\.coverage|\.DS_Store|.*\.swp|\.vscode/|\.idea/|node_modules/)|^!! (\.claude/(skills/|settings\.local\.json|scheduled_tasks\.lock)|\.impeccable/)'

# Echo a worktree's reap-BLOCKING local state (empty = safe to reap). `--ignored`
# surfaces ignored entries (`!! ` prefix) that `git worktree remove` would delete; we
# strip only the regenerable-allowlisted ones, leaving tracked/untracked changes AND
# any precious ignored file as residue. One check covers both dirtiness and the
# ignored-delete hazard.
_loop_gc_local_state() {
  git -C "$1" status --porcelain --ignored 2>/dev/null \
    | grep -vE "$_LOOP_GC_REGEN_IGNORED" \
    | grep -vE '^[[:space:]]*$'
}

# Decide the disposition of ONE worktree and act per MODE.
# Args: <path> <branch> <current_toplevel> <default_branch> <mode> <root>
#   mode=reap   → `git worktree remove` + log to the ledger (loop mode).
#   mode=report → echo "<path> (<branch>)" for a reapable candidate (HIL, read-only).
# Safe-subset gate (ALL must hold): not the current worktree; has a branch (not
# detached); not the default branch; branch's PR merged at the worktree's exact HEAD
# SHA; clean working tree (ignored-aware).
_loop_gc_consider() {
  local path="$1" branch="$2" current="$3" default="$4" mode="$5" root="$6"
  [ -n "$path" ] || return 0
  # Canonicalize the candidate the same way as `current` before the self-exclude compare
  # (codex P2). git ops below use the ORIGINAL $path (as git recorded it).
  local cpath; cpath=$(cd "$path" 2>/dev/null && pwd -P || printf '%s' "$path")
  [ "$cpath" = "$current" ] && return 0                      # never the current worktree
  [ -n "$branch" ] || return 0                               # detached HEAD → skip
  [ "$branch" = "$default" ] && return 0                     # never the default branch
  # Branch must be merged AND the worktree HEAD must equal the EXACT SHA that was merged.
  # Name-only matching would reap a reused/renamed clean branch whose new commits were
  # never merged (codex P2). headRefOid ties identity to the merged commit; squash-safe.
  local want_oid; want_oid=$(_loop_gc_merged_oid "$branch" "$root")
  [ -n "$want_oid" ] || return 0                             # branch has no merged PR → skip
  local head_oid; head_oid=$(git -C "$path" rev-parse HEAD 2>/dev/null)
  if [ "$head_oid" != "$want_oid" ]; then                    # local branch advanced/reused → not this PR
    [ "$mode" = "reap" ] && loop_log GC "skipped $path ($branch) — HEAD ${head_oid:0:8} != merged ${want_oid:0:8} (name collision/reuse)"
    return 0
  fi
  local residue; residue=$(_loop_gc_local_state "$path")     # dirty / untracked / precious-ignored
  if [ -n "$residue" ]; then
    [ "$mode" = "reap" ] && loop_log GC "skipped $path ($branch) — has local state: $(printf '%s' "$residue" | tr '\n' ',' | sed 's/^,//;s/,$//' | cut -c1-160)"
    return 0
  fi
  # A merged+clean worktree can still have a LIVE session attached — reaping it would
  # orphan that session (Edit/Write pinned to the deleted root). Never reap a live one.
  if worktree_has_live_session "$cpath"; then
    [ "$mode" = "reap" ] && loop_log GC "skipped $path ($branch) — live Claude session (recent transcript)"
    return 0
  fi
  if [ "$mode" = "report" ]; then
    printf '%s (%s)\n' "$path" "$branch"
    return 0
  fi
  if git -C "$root" worktree remove "$path" 2>/dev/null; then
    loop_log GC "reaped worktree $path (branch $branch merged+clean; branch ref left for operator)"
  else
    loop_log GC "skipped $path ($branch) — git worktree remove refused (locked/untracked)"
  fi
}

# Garbage-collect stale worktrees. WORKTREES ONLY; fail-safe to zero removals when the
# merged set is unavailable. Deterministic bash (NOT a Claude tool call) → bypasses
# permission-guard; the safe-subset gate above is the backstop. Always returns 0.
#   mode=reap   (default) → remove + log each disposition.
#   mode=report           → echo "<path> (<branch>)" per reapable candidate (read-only).
# Usage: loop_gc_worktrees [reap|report]
loop_gc_worktrees() {
  local mode="${1:-reap}"
  command -v git >/dev/null 2>&1 || return 0
  local root; root=$(hook_project_dir); [ -n "$root" ] || return 0
  # Fail-safe: if gh can't reach the API (offline/unauth), do nothing rather than treat
  # every branch as unmerged-vs-merged ambiguously. One upfront probe, not N.
  if ! _loop_gc_gh_ok "$root"; then
    [ "$mode" = "reap" ] && loop_log GC "skipped — gh unavailable (offline/unauth/not-installed); zero removals"
    return 0
  fi
  local current default
  current=$(git -C "$root" rev-parse --show-toplevel 2>/dev/null)
  # Canonicalize to a physical path so self-exclusion can't be defeated by a symlink /
  # /var-vs-/private/var spelling difference between rev-parse and `worktree list`
  # (codex P2: a mismatch would let the CURRENT worktree be reaped).
  current=$(cd "$current" 2>/dev/null && pwd -P || printf '%s' "$current")
  default=$(hook_default_branch)
  local path="" branch=""
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) path="${line#worktree }" ;;
      "branch refs/heads/"*) branch="${line#branch refs/heads/}" ;;
      "") _loop_gc_consider "$path" "$branch" "$current" "$default" "$mode" "$root"; path=""; branch="" ;;
    esac
  done < <(git -C "$root" worktree list --porcelain 2>/dev/null)
  # Trailing record safety-net (porcelain normally ends with a blank line).
  [ -n "$path" ] && _loop_gc_consider "$path" "$branch" "$current" "$default" "$mode" "$root"
  return 0
}

# ── Remote branch close-out (post-merge, per-arc) ──────────────────────────
# SCOPE (operator correction, 2026-07-15): the actual discipline is "delete
# THIS arc's own remote branch on GitHub right after its merge commit's
# post-merge CI on <default> is confirmed green" — not a local-ref scanning
# GC engine. An earlier version built a full local-branch-backlog scanner
# (bulk merged-PR index, per-branch CAS local delete, checked-out-worktree
# guard) cross-referenced against `git branch` — which reports on STALE
# LOCAL refs whose GitHub-side branch may already be long gone, producing
# misleading "N branches held" output entirely disconnected from the actual
# remote state (`.harness/post-phase-8-forward-register.md` and the
# session-level correction record it). Removed. The discipline operates on
# the REMOTE (GitHub) branch, is always a single named branch (the one just
# merged — no scanning/backlog concept applies), and is documented as a
# direct recipe in the `ship-pr` skill: verify CI green on the merge commit,
# then a LEASE-GUARDED `git push --force-with-lease=refs/heads/<branch>:<merged-oid>
# origin :refs/heads/<branch>` (never a bare `gh api -X DELETE`/`git push --delete`,
# which has no CAS guard and would silently destroy any new work pushed to the
# same branch name post-merge). Local branch refs are left alone entirely —
# they carry no unique value once merged (git reflog covers recovery for ~90
# days regardless) and are not what "branch hygiene" refers to in this
# workspace's discipline.
