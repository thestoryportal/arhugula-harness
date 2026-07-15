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

# ── Branch garbage collection (extends U-HK-26 to branch refs) ────────────────
# SCOPE (operator correction, 2026-07-15 — read this before touching the size
# of this section again): the actual ask is "clean up THIS arc's own branch
# right after its merge goes CI-green" — the 2-worktrees-once-merged pattern.
# An earlier version of this built a full historical-backlog GC engine
# instead (cursor persistence across runs, per-run mutation caps, a
# 5000-PR-limit bulk index, a freshness-window that skipped live CI checks
# for "old" branches) — scope far beyond the ask, and every extra piece of
# machinery was its own source of adversarial-review findings (verified: ~13
# review rounds, severity trending toward edge cases IN that machinery, not
# in the core safe-delete logic). Cut back down deliberately. If a large
# historical local-branch backlog needs clearing later, that is a distinct,
# smaller, one-off ask — not a reason to carry this complexity permanently.
#
# The reframe that makes branch deletion safe at all: once a branch's EXACT
# tip SHA is independently verified as a MERGED-INTO-<default> PR's
# headRefOid (the same squash-safe gate loop_gc_worktrees already uses via
# _loop_gc_merged_oid, base-qualified here), its content is provably already
# in <default> and the ref itself is reflog-recoverable for ~30 days —
# deleting it is effectively reversible.
#
# TRIGGER: NOT a SessionStart hook. The moment a branch is provably safe to
# delete is right after ITS OWN arc's post-merge CI on <default> goes green,
# in the SAME session that did the merging — that session already has the
# CI-green proof in hand. Primary caller: the `ship-pr` skill's post-merge
# close-out step (`just branch-hygiene-sweep`); also directly invocable for a
# manual pass. Worktree removal genuinely still has to wait for a later
# session (can't remove the worktree you're running inside) — unchanged,
# stays on loop_gc_worktrees/SessionStart.
#
# CI-green gate ("final merge to main CI green"): checked LIVE, always — no
# freshness-window exemption. Every branch this mechanism considers is, by
# construction, a RECENT merge (this session's own arc, or another recent one
# incidentally caught by the same scan) — GitHub Actions run-history has no
# retention concern at this scale, so there is no case where skipping the
# live check is warranted. A merged-PR *state* alone proves the PR's own
# PRE-merge checks passed, not that the resulting commit's POST-merge run on
# <default> is green (this repo's own history has a documented case of
# exactly that gap — see `.harness/post-phase-8-forward-register.md` B-28's
# 2026-07-14 entry) — the live check on the merge commit is the only thing
# that actually proves the operator's stated gate.

_loop_gc_branch_pr_limit="${_loop_gc_branch_pr_limit:-200}"

# ONE bulk gh call per loop_gc_branches invocation — recent PRs merged INTO
# <default> (not just any base — an unqualified query would match a PR merged
# into some OTHER integration/feature branch whose content never reached
# <default>), flattened straight to TSV by gh's own --jq (one
# "headRefName<TAB>headRefOid<TAB>mergeCommitOid" line per merged PR). --limit
# 200 covers this session's own arc plus any other recent merges in one
# request — this mechanism is no longer trying to cover full repo history
# (see the section header). Echoes the TSV; empty string on any failure
# (caller treats that the same as "no merged PRs found").
_loop_gc_merged_pr_tsv() {
  local root="$1" default="$2"
  ( cd "$root" 2>/dev/null || exit 0
    hook_bounded 15 gh pr list --state merged --base "$default" --limit "$_loop_gc_branch_pr_limit" \
      --json headRefName,headRefOid,mergeCommit \
      --jq '.[] | "\(.headRefName)\t\(.headRefOid // "")\t\(.mergeCommit.oid // "")"' 2>/dev/null )
}

# Look up ONE branch inside a pre-fetched TSV index (see above) — a plain
# `awk` linear scan over an in-memory string, zero network/JSON-parse per
# call. Echoes "headRefOid mergeCommitOid" (space-separated; either may be
# empty). Empty first field = no merged-into-<default> PR by this name.
_loop_gc_merge_info_from_index() {
  local branch="$1" tsv="$2"
  printf '%s\n' "$tsv" | awk -F'\t' -v b="$branch" '$1 == b { print $2, $3; exit }'
}

# CI conclusion for <sha>'s own workflow run(s) — <sha> must be the MERGE
# commit on <default> (the post-squash push-triggered run), not the pre-squash
# PR head, or this observes the wrong CI history entirely. 0=success(green),
# 1=non-success (red — do not reap), 2=unknown (no run found — caller
# decides; report mode never calls this). Bounded so a slow/offline API can't
# hang the hook. Still a live per-branch call, but the freshness gate below
# limits how often it fires (typically 0-2 candidates per run).
_loop_gc_ci_green_for_commit() {
  local sha="$1" root="$2" concl
  concl=$(cd "$root" 2>/dev/null && hook_bounded 6 gh run list --commit "$sha" \
            --json conclusion --jq '.[0].conclusion // empty' 2>/dev/null)
  case "$concl" in
    success) return 0 ;;
    "") return 2 ;;
    *) return 1 ;;
  esac
}

# True (0) iff <branch> is the current HEAD of ANY worktree (main checkout or a
# linked one) — such a branch is live work-in-progress and must never be
# force-deleted regardless of merge state (git would refuse anyway, but this
# gives a clean, loggable skip instead of a raw git error).
_loop_gc_branch_checked_out() {
  local branch="$1" root="$2"
  git -C "$root" worktree list --porcelain 2>/dev/null | grep -qxF "branch refs/heads/$branch"
}

# Decide the disposition of ONE branch and act per MODE. <index> is the
# pre-fetched merged-PR TSV from _loop_gc_merged_pr_tsv (empty = none
# available this run, e.g. gh degraded — every branch then skips as
# not-a-candidate, fail-safe). <checked_out_set> and <precomputed_tip> are
# OPTIONAL batch-precomputed values from loop_gc_branches' hot path (a
# newline-separated set of checked-out branch names, and this branch's own
# tip SHA) — passing them skips a `git worktree list` + `git rev-parse`
# subprocess per branch, which is the difference between an uncapped
# ~290-branch scan taking ~35s (all per-branch subprocess spawns) and being
# near-instant. Omit either to fall back to the single-branch subprocess path
# (what the direct unit-test calls below use, at small fixture scale where it
# doesn't matter).
#   mode=reap   → CAS local delete + lease-guarded remote delete + log.
#   mode=report → echo the branch name (read-only candidate list).
# Safe-subset gate (ALL must hold): not the default branch; not checked out in
# any worktree; branch's PR merged INTO <default> AT THE BRANCH'S EXACT TIP
# SHA (squash-safe, via the index's headRefOid — the same gate
# loop_gc_worktrees uses via _loop_gc_merged_oid, just base-qualified); if the
# merge is fresh (within the freshness window), its own CI conclusion on the
# actual merge commit is confirmed green.
# Note a degraded/held disposition (mode-aware): reap gets a ledger row
# (audit trail for the unattended ship-pr path); report gets stderr (its
# only caller is a direct interactive command — a silently-empty report is
# indistinguishable from "genuinely nothing to prune", codex P2).
_loop_gc_branch_note() {
  local mode="$1" branch="$2" msg="$3"
  if [ "$mode" = "reap" ]; then
    loop_log GC "skipped branch $branch — $msg"
  else
    echo "branch-hygiene-report: $branch — HELD ($msg)" >&2
  fi
}

_loop_gc_consider_branch() {
  local branch="$1" default="$2" mode="$3" root="$4" index="${5:-}"
  local checked_out_set="${6:-}" precomputed_tip="${7:-}"
  [ -n "$branch" ] || return 0
  case "$mode" in reap|report) : ;; *) return 0 ;; esac   # unrecognized mode → refuse (codex P1)
  [ "$branch" = "$default" ] && return 0
  if [ -n "$checked_out_set" ]; then
    printf '%s\n' "$checked_out_set" | grep -qxF "$branch" && return 0
  else
    _loop_gc_branch_checked_out "$branch" "$root" && return 0   # live in some worktree
  fi
  [ -n "$index" ] || return 0                                 # no index this run → fail-safe skip

  local info want_oid merge_oid
  info=$(_loop_gc_merge_info_from_index "$branch" "$index")
  read -r want_oid merge_oid <<< "$info"
  [ -n "$want_oid" ] || return 0                              # no merged-into-<default> PR by this name
  local tip_oid
  if [ -n "$precomputed_tip" ]; then
    tip_oid="$precomputed_tip"
  else
    tip_oid=$(git -C "$root" rev-parse "refs/heads/$branch" 2>/dev/null)
  fi
  [ "$tip_oid" = "$want_oid" ] || return 0                    # reused/advanced name → skip
  # The actual commit that landed on <default> (post-squash) is the ONLY
  # valid CI-check target for the "final merge to main CI green" gate — a
  # fallback to want_oid (the pre-squash PR head) would check the PR's
  # PRE-merge CI instead, which can be green while the actual post-merge
  # commit on <default> is red or still running (this repo's squash workflow
  # means headRefOid's own CI history says nothing about main's post-merge
  # state). Missing mergeCommit.oid must fail closed, not silently substitute
  # a different commit's CI history.
  if [ -z "$merge_oid" ]; then
    _loop_gc_branch_note "$mode" "$branch" "merged-PR index has no mergeCommit.oid (cannot verify post-merge CI on ${default})"
    return 0
  fi

  # Live CI check, unconditional — every branch this function considers is,
  # by construction, a recent merge (see section header), so there is no
  # "too old to check" case to exempt. A merged-PR state alone proves the
  # PR's PRE-merge checks passed, not that the resulting commit's POST-merge
  # run on <default> is green — this repo's own history has a documented
  # case of exactly that gap (main CI red for a full day while every
  # individual PR's own pre-merge checks were fine) — the live check on the
  # merge commit is the only thing that actually proves the stated gate.
  _loop_gc_ci_green_for_commit "$merge_oid" "$root"
  local ci_rc=$?
  if [ "$ci_rc" -ne 0 ]; then
    _loop_gc_branch_note "$mode" "$branch" "post-merge CI on ${default} not confirmed green for ${merge_oid:0:8} (rc=$ci_rc)"
    return 0
  fi

  if [ "$mode" = "report" ]; then
    printf '%s\n' "$branch"
    return 0
  fi

  # Re-check occupancy before starting the remote round-trip too (not just
  # right before the local delete below) — the network calls ahead take real
  # wall-clock time, exactly the window in which another process could check
  # this branch out (codex P1).
  _loop_gc_branch_checked_out "$branch" "$root" && { loop_log GC "skipped branch $branch — now checked out (race since snapshot)"; return 0; }

  # Remote FIRST, local SECOND — deliberately reversed from a naive
  # local-then-remote order. Once the local ref is gone, nothing keys a
  # retry of the remote side (this whole function is entered via the local
  # branch list) — so if the remote probe or delete fails/races, both refs
  # must be left intact for a future run to pick back up, not just the
  # remote one (codex P2). Bounded, non-interactive (GIT_TERMINAL_PROMPT=0
  # so a missing credential helper can't hang on a prompt).
  # A BARE branch name as the ls-remote pattern arg does suffix/glob matching
  # (e.g. "foo" also matches "refs/heads/team/foo"), which could return
  # multiple lines and either wrongly retain a distinct remote ref or block
  # deletion of the intended one (codex P2). The fully-qualified
  # "refs/heads/$branch" pattern matches exactly.
  local remote_line remote_rc remote_oid=""
  remote_line=$(cd "$root" 2>/dev/null \
    && GIT_TERMINAL_PROMPT=0 hook_bounded 8 git ls-remote --heads origin "refs/heads/$branch" 2>/dev/null)
  remote_rc=$?
  remote_oid=$(printf '%s\n' "$remote_line" | awk 'NR==1{print $1}')
  if [ "$remote_rc" -ne 0 ]; then
    # A network/auth failure is NOT the same as "the branch legitimately has
    # no remote ref" — treating it as such (as an earlier version of this
    # code did) would delete local and permanently strand an un-probed
    # remote branch with nothing left to key a retry off (codex P2).
    loop_log GC "skipped branch $branch — remote probe failed (rc=$remote_rc), left both refs intact for retry"
    return 0
  fi

  local remote_disposition
  if [ -z "$remote_oid" ]; then
    remote_disposition="remote already gone"
  elif [ "$remote_oid" != "$want_oid" ]; then
    remote_disposition="remote tip ${remote_oid:0:8} != merged ${want_oid:0:8} — left remote alone, possible reuse/new work"
  else
    # --force-with-lease is the atomic CAS guard on the PUSH itself: the
    # delete fails outright if the remote's tip changed between the probe
    # above and this push (codex P1) — a plain `--delete` has no such
    # guarantee, and re-probing right before push would still leave a
    # (much smaller) gap.
    if GIT_TERMINAL_PROMPT=0 hook_bounded 10 git -C "$root" push \
         --force-with-lease="refs/heads/${branch}:${want_oid}" origin ":refs/heads/${branch}" >/dev/null 2>&1; then
      remote_disposition="local+remote"
    else
      loop_log GC "skipped branch $branch — remote delete failed/raced, left both refs intact for retry"
      return 0
    fi
  fi

  # Re-check occupancy IMMEDIATELY before deletion, not just against the
  # start-of-run snapshot — `update-ref -d` has no built-in checked-out
  # guard the way `git branch -D` does, and the remote probe/push above (a
  # real network round trip) is exactly the kind of window in which another
  # process could have checked this branch out since the snapshot was taken
  # (codex P1).
  _loop_gc_branch_checked_out "$branch" "$root" && { loop_log GC "skipped branch $branch — now checked out (race since snapshot)"; return 0; }

  # CAS-delete: `update-ref -d <ref> <oldvalue>` refuses (ref left untouched)
  # if the ref no longer equals want_oid — closes the probe-then-delete race
  # window a plain `git branch -D` leaves open. Only reached once the remote
  # side is resolved (deleted, confirmed gone, or deliberately left alone for
  # a name-collision reason).
  #
  # Residual (accepted, not fixed): a checkout landing in the few
  # milliseconds between the recheck above and this exact command is still
  # possible — `update-ref -d` has no atomic checked-out guard the way
  # `git branch -D` does, and there is no single git primitive that offers
  # both a SHA-CAS guarantee AND a checkout guard. Closing this fully would
  # need a lock file or similar, for a window this workspace's actual usage
  # pattern (single operator, sequential Claude sessions, not concurrent
  # multi-agent writers to the same branch name) makes vanishingly unlikely.
  # The occupancy recheck immediately above already narrows the exposure from
  # "whole scan duration" to "a few git syscalls" — judged good enough given
  # the actual risk profile; not chasing full atomicity further.
  if git -C "$root" update-ref -d "refs/heads/$branch" "$want_oid" >/dev/null 2>&1; then
    loop_log GC "reaped branch $branch (${remote_disposition}; merged @ ${want_oid:0:8})"
  else
    loop_log GC "skipped branch $branch — ref moved since verification (race) or update-ref refused"
  fi
}

# Garbage-collect merged branch refs (local + remote, U-HK-26 extension). Same
# fail-safe gh-probe contract as loop_gc_worktrees: gh unavailable → zero
# removals. Deterministic bash (still runs as a normal Bash tool invocation
# via the `just branch-hygiene-sweep`/`-report` recipes — no permission-guard
# allowlist bypass; branch deletion goes through the standard ask-approval
# gate each time, matching the "explicit request per destructive action"
# discipline this workspace's Git Safety Protocol requires).
#   mode=reap   (default) → delete + log each disposition.
#   mode=report            → echo candidate branch names (read-only).
# Usage: loop_gc_branches [reap|report]
loop_gc_branches() {
  local mode="${1:-reap}"
  # A mistyped mode (e.g. "reports") must NOT silently fall through to
  # destructive behavior — every mode-dispatch in _loop_gc_consider_branch is
  # written as "if this exact string, do X" with no explicit else.
  case "$mode" in
    reap|report) : ;;
    *)
      loop_log GC "branch-gc: unrecognized mode '$mode' — refusing to run (expected reap|report)"
      return 0
      ;;
  esac
  command -v git >/dev/null 2>&1 || return 0
  local root; root=$(hook_project_dir); [ -n "$root" ] || return 0
  # Report mode's caller (`just branch-hygiene-report`) is a direct
  # interactive command — silently returning empty on a gh failure reads
  # identically to "genuinely nothing to prune". Surface it on stderr, not
  # just the ledger (which reap already gets via loop_log).
  if ! _loop_gc_gh_ok "$root"; then
    if [ "$mode" = "reap" ]; then
      loop_log GC "branch-gc skipped — gh unavailable (offline/unauth/not-installed); zero removals"
    else
      echo "branch-hygiene-report: gh unavailable (offline/unauth/not-installed) — result is UNKNOWN, not \"nothing to prune\"" >&2
    fi
    return 0
  fi
  local default; default=$(hook_default_branch)
  local index; index=$(_loop_gc_merged_pr_tsv "$root" "$default")
  if [ -z "$index" ]; then
    if [ "$mode" = "reap" ]; then
      loop_log GC "branch-gc skipped — merged-PR index unavailable this run; zero removals"
    else
      echo "branch-hygiene-report: merged-PR index fetch failed (gh reachable but the query itself errored/timed out) — result is UNKNOWN, not \"nothing to prune\"" >&2
    fi
    return 0
  fi

  # Batch-precompute per-branch data ONCE (not per-branch): a `git worktree
  # list` / `git rev-parse` per branch adds up even at the small scale this
  # mechanism now targets (a handful of local branches, not a large
  # backlog) — two calls up front instead of 2N is a cheap, unconditional win.
  local checked_out_set
  checked_out_set=$(git -C "$root" worktree list --porcelain 2>/dev/null | sed -n 's#^branch refs/heads/##p')

  local -a branches=() branch_shas=()
  while IFS=$'\t' read -r b sha; do
    [ -n "$b" ] || continue
    branches+=("$b")
    branch_shas+=("$sha")
  done < <(git -C "$root" branch --format='%(refname:short)%09%(objectname)' 2>/dev/null)
  local n=${#branches[@]}
  [ "$n" -gt 0 ] || return 0

  local idx
  for (( idx = 0; idx < n; idx++ )); do
    _loop_gc_consider_branch "${branches[$idx]}" "$default" "$mode" "$root" "$index" "$checked_out_set" "${branch_shas[$idx]}"
  done
  return 0
}
