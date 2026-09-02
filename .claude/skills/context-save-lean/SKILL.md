---
name: context-save-lean
description: Save working context to this workspace's checkpoint directory (~/.gstack/projects/arhugula-v2/checkpoints/) — the trimmed workspace copy of the gstack /context-save save flow, without the gstack preamble (U-SR-08, charter WR-15). Use at every arc close (ship-pr reflect step 4), near compaction, or before a risky operation; the file it writes is loadable by the user-level gstack /context-restore.
---

# /context-save-lean — save working context (workspace copy)

The save flow of the gstack `context-save` skill, cut to what this workspace uses. The
gstack skill injects ~54 KB per invocation; everything before its save flow is preamble for
sinks this workspace never touches (artifacts sync, brain sync, telemetry, plan-mode
routing, skill routing), and the only sink actually used is the local checkpoint directory
(U-SR-08, charter WR-15, audit [B] F11). This copy carries no preamble.

Why a new name: a personal skill overrides a project skill of the same name (Claude Code
skills doc, "personal overrides project"), so a project-level `context-save` would never
run — the workspace's own callers (ship-pr, roadmap-continue) invoke this skill by this name.

Two properties this copy holds because other tools depend on them:

- The checkpoint directory, filename shape, and file format are the gstack ones, so the
  user-level gstack `/context-restore` loads these files unchanged.
- The confirmation block carries a `File:` line naming the PUBLISHED path; ship-pr passes
  that exact path to `just arc-exit-report --checkpoint`, which is what binds the exit report
  to this arc.

**HARD GATE:** Do NOT implement code changes. This skill captures state only.

---

## Detect command

- `/context-save-lean` or `/context-save-lean <title>` → **Save**
- `/context-save-lean list` → **List**

A title given after the command is used as-is. Otherwise infer a concise title (3–6
words) from the current work.

`resume` / `restore` are not modes here: point the user at the user-level gstack
`/context-restore`.

---

## Save flow

### Step 1: Gather state

```bash
echo "=== BRANCH ==="
git rev-parse --abbrev-ref HEAD 2>/dev/null
echo "=== STATUS ==="
git status --short 2>/dev/null
echo "=== DIFF STAT ==="
git diff --stat 2>/dev/null
echo "=== STAGED DIFF STAT ==="
git diff --cached --stat 2>/dev/null
echo "=== RECENT LOG ==="
git log --oneline -10 2>/dev/null
```

### Step 2: Summarize context

From the gathered state plus the conversation, produce:

1. **What's being worked on** — the high-level goal or feature
2. **Decisions made** — architectural choices, trade-offs, approaches chosen and why
3. **Remaining work** — concrete next steps, in priority order
4. **Notes** — anything a future session needs (gotchas, blocked items, open questions,
   things tried that didn't work)

Workspace rules for the content:

- **Remaining Work is advisory.** `.harness/roadmap_status.md` supersedes checkpoints for
  cross-session next-action derivation (CLAUDE.md §12.5). Write the remaining work anyway;
  the resuming session re-grounds it against the dashboard, never the other way round.
- **A facts brief rides in Notes.** When the ship-pr reflect step produced a facts brief
  for a heavy next item (U-SR-07/WR-14), paste it under Notes verbatim — this save is what
  carries it to the fresh session that authors from it.

### Step 3: Compute session duration

```bash
START_EPOCH=$(ps -o lstart= -p $PPID 2>/dev/null | xargs -I{} date -jf "%c" "{}" "+%s" 2>/dev/null || echo "")
if [ -n "$START_EPOCH" ]; then
  echo "SESSION_DURATION_S=$(( $(date +%s) - START_EPOCH ))"
else
  echo "SESSION_DURATION_S=unknown"
fi
```

If the duration is unknown, omit the `session_duration_s` field from the file.

### Step 4: Write the checkpoint file

Compute every path in bash, never in the LLM layer. Two blocks bracket the Write: **4a**
allocates a hidden staging path, the Write tool fills it, **4b** publishes it under its
final `.md` name by `link(2)` — so a `*.md` file either does not exist or is complete, and
two sessions can never share a name.

Run each block as ONE Bash command: its inputs as plain single-quoted assignments on the
first line(s), then the block verbatim — never wrapped in `bash -c '…'` (the blocks contain
single quotes, which would split the outer string). The filename sanitizer is an allowlist
(only `a-z 0-9 - .` survive) but it runs inside the shell, so the raw title reaches it
single-quoted with any single quotes removed:

```
TITLE_RAW='<title, any single quotes removed>'
<block 4a verbatim>
```

WRONG: `TITLE_RAW="<title>"` or `TITLE_RAW="$TITLE"` — double quotes expand `$(...)` and
backticks before the sanitizer ever sees them. WRONG: `bash -c '<block>'`.

**4a — allocate**

```bash
# Slug = the MAIN checkout's directory name, resolved through the git common dir so a
# linked worktree lands in the same sink (arhugula-v2 — the first slug
# tools/arc_exit_report.py searches). Any failure of that resolution is FATAL: an empty
# result would otherwise collapse to "." through dirname/basename, pass the allowlist,
# and write recovery state to projects/./checkpoints exactly when repository resolution
# is broken.
COMMON=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || COMMON=""
SLUG=$(basename "$(dirname "$COMMON")" | tr -cd 'a-zA-Z0-9._-')
case "$COMMON:$SLUG" in
  :*|*:|*:.|*:..) echo "FATAL: could not derive the project slug (git common dir: '${COMMON:-none}')"; exit 1 ;;
esac
CHECKPOINT_DIR="${GSTACK_STATE_ROOT:-$HOME/.gstack}/projects/$SLUG/checkpoints"
mkdir -p "$CHECKPOINT_DIR"
# TIMESTAMP is overridable (the trim witness pins a same-second collision); digits and
# hyphens only, empty falls back to now.
TIMESTAMP=$(printf '%s' "${TIMESTAMP:-}" | tr -cd '0-9-'); TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
RAW="${TITLE_RAW:-untitled}"
TITLE_SLUG=$(printf '%s' "$RAW" | tr '[:upper:]' '[:lower:]' | tr -s ' \t' '-' | tr -cd 'a-z0-9.-' | cut -c1-60)
TITLE_SLUG="${TITLE_SLUG:-untitled}"
# Staging path: a DOTFILE with a random token — no `*.md` listing (this skill's list flow,
# gstack /context-restore, arc_exit_report) can ever see it, and it is never a restorable
# checkpoint. It is not created here: the Write tool creates it in one step, so there is
# no empty file at any moment under a name anything reads.
TOKEN=$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom 2>/dev/null | head -c 6 || printf '%06x' "$$")
PART="${CHECKPOINT_DIR}/.${TIMESTAMP}-${TITLE_SLUG}-${TOKEN}.part"
echo "CHECKPOINT_DIR=$CHECKPOINT_DIR"
echo "TIMESTAMP=$TIMESTAMP"
echo "PART=$PART"
echo "FILE=${CHECKPOINT_DIR}/${TIMESTAMP}-${TITLE_SLUG}.md"
```

Write the full checkpoint content to the `$PART` path printed above (the exact string; a
new file, so the Write tool needs no prior Read). Then publish it:

**4b — publish** (first lines: `PART='<printed PART>'` and `FILE='<printed FILE>'`)

```bash
# Publish = link(2): exclusive on the final name, atomic, and only ever of a COMPLETE
# file. Two sessions saving the same title in the same second cannot end up on one
# name — the loser gets a random suffix; a lost third try is FATAL, never an overwrite.
# An empty or missing staging file means the Write never happened: refuse.
[ -s "$PART" ] || { echo "FATAL: staging file $PART is missing or empty — nothing to publish"; exit 1; }
tries=0
until ln "$PART" "$FILE" 2>/dev/null; do
  # Only an EXISTING final name is a collision; any other link failure is its own FATAL.
  [ -e "$FILE" ] || { echo "FATAL: cannot publish $FILE (is $(dirname "$FILE") writable?)"; exit 1; }
  tries=$((tries + 1))
  [ "$tries" -lt 3 ] || { echo "FATAL: could not publish after 3 name collisions"; exit 1; }
  SUFFIX=$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom 2>/dev/null | head -c 4 || printf '%04x' "$$")
  FILE="${FILE%.md}-${SUFFIX}.md"
done
rm -f "$PART"
echo "FILE=$FILE"
```

The published `FILE` is what the confirmation block reports. A crash between the Write and
4b leaves only a `.part` dotfile — invisible to every `*.md` listing; delete it on sight,
never publish it by hand. The directory name is `checkpoints/`; the gstack restore side
keys on the `YYYYMMDD-HHMMSS` filename prefix, so keep the shape.

The file format (identical to gstack's, which is what keeps it restorable):

```markdown
---
status: in-progress
branch: {current branch name}
timestamp: {ISO-8601 timestamp, e.g. 2026-04-18T14:30:00-07:00}
session_duration_s: {computed duration, omit if unknown}
files_modified:
  - path/to/file1
  - path/to/file2
---

## Working on: {title}

### Summary

{1-3 sentences describing the high-level goal and current progress}

### Decisions Made

{Bulleted list of architectural choices, trade-offs, and reasoning}

### Remaining Work

{Numbered list of concrete next steps, in priority order}

### Notes

{Gotchas, blocked items, open questions, things tried that didn't work; the facts brief when one exists}
```

`files_modified` comes from `git status --short` (staged and unstaged), as repo-relative
paths.

After writing, confirm to the user:

```
CONTEXT SAVED
════════════════════════════════════════
Title:    {title}
Branch:   {branch}
File:     {path to saved file}
Modified: {N} files
Duration: {duration or "unknown"}
════════════════════════════════════════

Restore later with /context-restore.
```

---

## List flow

```bash
COMMON=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || COMMON=""
SLUG=$(basename "$(dirname "$COMMON")" | tr -cd 'a-zA-Z0-9._-')
case "$COMMON:$SLUG" in
  :*|*:|*:.|*:..) echo "FATAL: could not derive the project slug (git common dir: '${COMMON:-none}')"; exit 1 ;;
esac
CHECKPOINT_DIR="${GSTACK_STATE_ROOT:-$HOME/.gstack}/projects/$SLUG/checkpoints"
# Three outcomes, kept apart: no directory / empty directory -> NO_CHECKPOINTS; a directory
# that exists but cannot be read or listed -> FATAL ("no contexts" must never stand in for
# "could not look"). find + sort, not ls -1t: the YYYYMMDD-HHMMSS prefix is the canonical order.
if [ ! -d "$CHECKPOINT_DIR" ]; then
  echo "NO_CHECKPOINTS"
else
  echo "CHECKPOINT_DIR=$CHECKPOINT_DIR"
  [ -r "$CHECKPOINT_DIR" ] && [ -x "$CHECKPOINT_DIR" ] || { echo "FATAL: cannot read $CHECKPOINT_DIR"; exit 1; }
  LIST=$(find "$CHECKPOINT_DIR" -maxdepth 1 -name "*.md" -type f) || { echo "FATAL: listing $CHECKPOINT_DIR failed"; exit 1; }
  if [ -n "$LIST" ]; then printf '%s\n' "$LIST" | sort -r; else echo "NO_CHECKPOINTS"; fi
fi
```

Show the current branch's contexts by default; `--all` shows every branch (add a Branch
column). Read `status`, `branch`, `timestamp` from each file's frontmatter; the title is
the filename after the timestamp.

```
SAVED CONTEXTS ({branch} branch)
════════════════════════════════════════
#  Date        Title                    Status
─  ──────────  ───────────────────────  ───────────
1  2026-04-18  auth-refactor            in-progress
════════════════════════════════════════
```

`NO_CHECKPOINTS` → "No saved contexts yet. Run `/context-save-lean` to save your current
working state." A `FATAL:` line means discovery FAILED — report that failure verbatim, never
"no contexts".

---

## Important rules

- **Never modify code.** Read state, write the context file, nothing else.
- **Always include the branch name** in frontmatter — cross-branch `/context-restore`
  depends on it.
- **Saved files are append-only.** Never overwrite or delete an existing checkpoint; each
  save is a new file.
- **Infer, don't interrogate.** Fill the file from git state and the conversation; ask only
  if the title genuinely cannot be inferred.
- **Never `/context-save`** from a workspace skill: that name resolves to the user-level
  gstack skill and re-injects the ~54 KB preamble this copy exists to drop.
