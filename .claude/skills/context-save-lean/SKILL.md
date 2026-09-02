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
- The confirmation block ends with the `File:` line; ship-pr passes that exact path to
  `just arc-exit-report --checkpoint`, which is what binds the exit report to this arc.

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

Compute the path in bash, never in the LLM layer, so a user-supplied title cannot inject
shell metacharacters into a later command. The sanitizer is an allowlist: only
`a-z 0-9 - .` survive.

```bash
# Slug = the MAIN checkout's directory name, resolved through the git common dir so a
# linked worktree lands in the same sink (arhugula-v2 — the first slug
# tools/arc_exit_report.py searches). Fail loud on an empty slug rather than writing to
# projects//checkpoints.
SLUG=$(basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")" | tr -cd 'a-zA-Z0-9._-')
[ -n "$SLUG" ] || { echo "FATAL: could not derive the project slug"; exit 1; }
CHECKPOINT_DIR="${GSTACK_STATE_ROOT:-$HOME/.gstack}/projects/$SLUG/checkpoints"
mkdir -p "$CHECKPOINT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
# Pass the raw title as TITLE_RAW when running this block: TITLE_RAW="u-sr-08 closed" bash -c '...'
RAW="${TITLE_RAW:-untitled}"
TITLE_SLUG=$(printf '%s' "$RAW" | tr '[:upper:]' '[:lower:]' | tr -s ' \t' '-' | tr -cd 'a-z0-9.-' | cut -c1-60)
TITLE_SLUG="${TITLE_SLUG:-untitled}"
# Append-only: a same-second save with the same title gets a random suffix, never an overwrite.
FILE="${CHECKPOINT_DIR}/${TIMESTAMP}-${TITLE_SLUG}.md"
if [ -e "$FILE" ]; then
  SUFFIX=$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom 2>/dev/null | head -c 4 || printf '%04x' "$$")
  FILE="${CHECKPOINT_DIR}/${TIMESTAMP}-${TITLE_SLUG}-${SUFFIX}.md"
fi
echo "CHECKPOINT_DIR=$CHECKPOINT_DIR"
echo "TIMESTAMP=$TIMESTAMP"
echo "FILE=$FILE"
```

Write the file to the `$FILE` path printed above — the exact string, not a path rebuilt in
the LLM layer. The directory name is `checkpoints/`; the gstack restore side keys on the
`YYYYMMDD-HHMMSS` filename prefix, so keep the shape.

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
SLUG=$(basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")" | tr -cd 'a-zA-Z0-9._-')
CHECKPOINT_DIR="${GSTACK_STATE_ROOT:-$HOME/.gstack}/projects/$SLUG/checkpoints"
if [ -d "$CHECKPOINT_DIR" ]; then
  echo "CHECKPOINT_DIR=$CHECKPOINT_DIR"
  # find + sort, not ls -1t: the YYYYMMDD-HHMMSS prefix is the canonical order.
  find "$CHECKPOINT_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | sort -r
else
  echo "NO_CHECKPOINTS"
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

No files → "No saved contexts yet. Run `/context-save-lean` to save your current
working state."

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
