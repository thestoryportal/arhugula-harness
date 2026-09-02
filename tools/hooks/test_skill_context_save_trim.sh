#!/usr/bin/env bash
# Witness for U-SR-08 leg 1 (charter WR-15): the context-save preamble trim. The gstack
# `context-save` skill injects ~54 KB per invocation ([B] F11: 53.8 KB; 54,977 bytes on the
# operator host, gstack context-save 1.0.0 as installed 2026-09-01), of which only the save
# flow (that file's lines 784-1028, ~9.5 KB) is
# used here — the rest is preamble for sinks this workspace never touches. The lever is a
# project skill carrying the save flow only. It CANNOT be named `context-save`: per the
# Claude Code skills doc ("Across levels, enterprise overrides personal, and personal
# overrides project"), a same-named personal skill wins, so the project copy would never
# run — and the command comes from the DIRECTORY name ("`name` sets only the display
# label"). Hence `context-save-lean`, with the workspace's own callers (ship-pr,
# roadmap-continue) pointed at it.
#
# Assertions run against the REAL checked-in files (the artifact under test IS the skill
# text), whitespace-normalized where a phrase spans lines. Three groups: (1) the skill's
# identity + size, (2) trim (preamble absent) + save-flow carriers present, (3) the callers
# invoke the workspace name and no longer instruct the shadowed `/context-save`. Plus two
# executable controls: every fenced bash block parses, and the Step-4 slug derivation
# resolves a linked worktree to the MAIN checkout's directory name (the arc_exit_report
# sink), which is the property the prose claims.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/../.."
SKILLS="$ROOT/.claude/skills"
SKILL="$SKILLS/context-save-lean/SKILL.md"
SHIP="$SKILLS/ship-pr/SKILL.md"
CONT="$SKILLS/roadmap-continue/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$SKILL" "$SHIP" "$CONT"; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done

# --- 1. identity + size -------------------------------------------------------------
# The command name is the directory name; the frontmatter name must agree so the listing
# label and the invocation never diverge.
NAME=$(awk 'NR>1 && /^---$/ {exit} /^name:/ {sub(/^name:[ \t]*/, ""); print}' "$SKILL")
[ "$NAME" = "context-save-lean" ] && ok "frontmatter name is context-save-lean (matches the directory)" \
  || bad "frontmatter name '$NAME' != directory name context-save-lean"
# A project-level `context-save` would be shadowed by the personal gstack skill and silently
# never run — its presence would mean the trim is inert.
[ ! -e "$SKILLS/context-save" ] && ok "no shadowed project-level context-save/ directory" \
  || bad "$SKILLS/context-save exists — personal overrides project, so it can never run"

# Byte cap. Derivation (WR-05: bounds cite their source): [B] F11 baseline is 53.8 KB
# (54,977 bytes measured); the used subset — the gstack save flow, lines 784-1028 — is
# ~9.5 KB. 16,384 bytes is under 30% of the baseline and leaves room for the two workspace
# rules. Breaching it means preamble crept back, which is the regression this pins.
CAP=16384
BYTES=$(wc -c < "$SKILL" | tr -d ' ')
echo "  measure: context-save-lean/SKILL.md = $BYTES bytes (cap $CAP; [B] F11 baseline 54,977)"
[ "$BYTES" -le "$CAP" ] && ok "skill body is $BYTES bytes <= $CAP" || bad "skill body is $BYTES bytes > $CAP (preamble crept back?)"
USER_SKILL="$HOME/.claude/skills/context-save/SKILL.md"
if [ -f "$USER_SKILL" ]; then
  UB=$(wc -c < "$USER_SKILL" | tr -d ' ')
  echo "  measure: user-level context-save/SKILL.md = $UB bytes (the before figure on this host)"
  [ "$BYTES" -lt "$UB" ] && ok "workspace copy ($BYTES) is smaller than the user-level skill ($UB)" \
    || bad "workspace copy ($BYTES) is not smaller than the user-level skill ($UB)"
else
  echo "  note: no user-level context-save skill on this host — before/after size comparison not run (1 check)"
fi

# --- 2. trim: preamble absent, save-flow carriers present ---------------------------
NORM=$(tr '\n' ' ' < "$SKILL" | tr -s ' ')
for h in '## Preamble' '## Artifacts Sync' '## Telemetry' '## AskUserQuestion Format' \
         '## Skill routing' 'gbrain' '## Voice' '## Plan Status Footer' 'AUTO-GENERATED' \
         '## Model-Specific Behavioral Patch' '## First-run guidance'; do
  printf '%s' "$NORM" | grep -qF -- "$h" && bad "preamble fragment present: $h" || ok "preamble fragment absent: $h"
done
for n in 'projects/$SLUG/checkpoints' '--git-common-dir' 'FATAL: could not derive the project slug' \
         'status: in-progress' 'branch: {current branch name}' 'timestamp: {ISO-8601' 'files_modified:' \
         'CONTEXT SAVED' 'File: {path to saved file}' 'Restore later with /context-restore' \
         'append-only' 'supersedes checkpoints' 'CLAUDE.md §12.5' 'facts brief' \
         'personal overrides project'; do
  printf '%s' "$NORM" | grep -qF -- "$n" && ok "carrier present: $n" || bad "carrier missing: $n"
done

# --- 3. callers invoke the workspace name; the shadowed name is no longer instructed ---
# ship-pr reflect block (section-scoped, u-sr-07 precedent: a whole-file match lets a
# relocated line stay green).
ship_reflect=$(awk '/^## Reflect/ {f=1} f && /^## Arc exit report/ {exit} f' "$SHIP" | tr '\n' ' ' | tr -s ' ')
ship_exit=$(awk '/^## Arc exit report/ {f=1} f && /^## Notes/ {exit} f' "$SHIP" | tr '\n' ' ' | tr -s ' ')
[ -n "$ship_reflect" ] && [ -n "$ship_exit" ] || { echo "FATAL: ship-pr section anchors moved"; exit 1; }
printf '%s' "$ship_reflect" | grep -qF -- '4. **Run `/context-save-lean`**' \
  && ok "ship-pr step 4 runs /context-save-lean" || bad "ship-pr step 4 does not run /context-save-lean"
printf '%s' "$ship_exit" | grep -qF -- '--checkpoint <the-path-/context-save-lean-just-reported>' \
  && ok "ship-pr exit report binds the workspace save's reported path" || bad "ship-pr exit report does not bind the workspace save path"
cont_step6=$(awk '/^6[.] [*][*]Ship/ {f=1} f && /^## / {exit} f' "$CONT" | tr '\n' ' ' | tr -s ' ')
[ -n "$cont_step6" ] || { echo "FATAL: roadmap-continue step 6 anchor moved"; exit 1; }
printf '%s' "$cont_step6" | grep -qF -- '`/context-save-lean`' \
  && ok "roadmap-continue step 6 names /context-save-lean" || bad "roadmap-continue step 6 does not name /context-save-lean"
# The exact shadowed invocation (closing backtick) must be gone from both carriers; the
# bare word `context-save` may remain in prose that names the gstack family.
for f in "$SHIP" "$CONT"; do
  if grep -qF -- '`/context-save`' "$f"; then
    bad "$(basename "$(dirname "$f")") still instructs the shadowed \`/context-save\`"
  else
    ok "$(basename "$(dirname "$f")") no longer instructs the shadowed \`/context-save\`"
  fi
done

# --- 4. executable controls -----------------------------------------------------------
# 4a. every fenced ```bash block parses (a typo in the recipe fails here, not at arc close).
TMPD="$(mktemp -d)"; { [ -n "$TMPD" ] && [ -d "$TMPD" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$TMPD"' EXIT
awk -v d="$TMPD" '
  /^```bash$/ {n++; f=d "/block" n ".sh"; inb=1; next}
  /^```$/ && inb {inb=0; close(f); next}
  inb {print > f}
' "$SKILL"
NB=$(ls "$TMPD"/block*.sh 2>/dev/null | wc -l | tr -d ' ')
[ "$NB" -ge 4 ] && ok "extracted $NB fenced bash blocks" || bad "expected >=4 fenced bash blocks, found $NB"
for b in "$TMPD"/block*.sh; do
  bash -n "$b" 2>/dev/null && ok "parses: $(basename "$b")" || bad "syntax error in $(basename "$b")"
done

# 4b. the Step-4 slug line resolves a linked worktree to the MAIN checkout's directory
#     name — the sink tools/arc_exit_report.py searches first (repo_root.name).
SLUG_LINE=$(grep -m1 '^SLUG=\$(basename' "$SKILL")
[ -n "$SLUG_LINE" ] || { bad "Step-4 SLUG line not found"; SLUG_LINE='SLUG='; }
REPO="$TMPD/wsroot/slug-probe-main"; mkdir -p "$REPO"
git -C "$REPO" init -q 2>/dev/null
git -C "$REPO" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init 2>/dev/null
git -C "$REPO" worktree add -q "$TMPD/wsroot/linked-wt" -b probe-wt 2>/dev/null
MAIN_SLUG=$(cd "$REPO" && eval "$SLUG_LINE" && printf '%s' "$SLUG")
WT_SLUG=$(cd "$TMPD/wsroot/linked-wt" && eval "$SLUG_LINE" && printf '%s' "$SLUG")
[ "$MAIN_SLUG" = "slug-probe-main" ] && ok "slug from the main checkout = slug-probe-main" || bad "main-checkout slug was '$MAIN_SLUG'"
[ "$WT_SLUG" = "slug-probe-main" ] && ok "slug from a linked worktree = slug-probe-main (not the worktree name)" || bad "worktree slug was '$WT_SLUG'"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
