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
AGENTS="$ROOT/.agents/skills"
ASHIP="$AGENTS/ship-pr/SKILL.md"
ACONT="$AGENTS/roadmap-continue/SKILL.md"
ALOOP="$AGENTS/codex-autonomous-loop/SKILL.md"
ABRIDGE="$AGENTS/context-save-lean/SKILL.md"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

for f in "$SKILL" "$SHIP" "$CONT" "$ASHIP" "$ACONT" "$ALOOP" "$ABRIDGE"; do
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
         'append-only' 'set -o noclobber' "TITLE_RAW='" 'supersedes checkpoints' 'CLAUDE.md §12.5' \
         'facts brief' 'personal overrides project'; do
  printf '%s' "$NORM" | grep -qF -- "$n" && ok "carrier present: $n" || bad "carrier missing: $n"
done

# The double-quoted title shape expands $(...) before the sanitizer runs (codex r1 P2): the
# only documented handoff is single-quoted, and the WRONG example carries no live command.
printf '%s' "$NORM" | grep -qF -- 'TITLE_RAW="$TITLE"' && ok "WRONG example names the double-quoted shape" || bad "WRONG double-quoted example missing"
printf '%s' "$NORM" | grep -qF -- "TITLE_RAW=\"<raw title>\" bash" && bad "a double-quoted TITLE_RAW handoff is still documented" || ok "no double-quoted TITLE_RAW handoff documented"

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
# Codex mirrors (codex r1 P2: a bridge nobody invokes is orphaned — the .agents carriers
# must name the lean skill at their own close-out moments, not the gstack one).
printf '%s' "$(tr '\n' ' ' < "$ASHIP" | tr -s ' ')" | grep -qF -- 'reflect on new recurrent lessons and run the `context-save-lean` skill' \
  && ok "codex ship-pr close-out runs context-save-lean" || bad "codex ship-pr close-out does not run context-save-lean"
printf '%s' "$(tr '\n' ' ' < "$ASHIP" | tr -s ' ')" | grep -qF -- '--checkpoint <the-path-context-save-lean-just-reported>' \
  && ok "codex ship-pr exit report binds the lean save path" || bad "codex ship-pr exit report does not bind the lean save path"
grep -qF -- 'reflect, and run the `context-save-lean` skill' "$ACONT" \
  && ok "codex roadmap-continue close-out runs context-save-lean" || bad "codex roadmap-continue close-out does not run context-save-lean"
grep -qF -- '20. Reflect and run the `context-save-lean` skill' "$ALOOP" \
  && ok "codex autonomous-loop step 20 runs context-save-lean" || bad "codex autonomous-loop step 20 does not run context-save-lean"
grep -qF -- '.claude/skills/context-save-lean/SKILL.md' "$ABRIDGE" \
  && ok "codex bridge names the canonical lean skill" || bad "codex bridge does not name the canonical lean skill"
for f in "$ASHIP" "$ACONT" "$ALOOP"; do
  grep -qF -- 'gstack `context-save` skill' "$f" && bad "$(basename "$(dirname "$f")") (codex) still instructs the gstack context-save skill" \
    || ok "$(basename "$(dirname "$f")") (codex) no longer instructs the gstack context-save skill"
done

# The exact shadowed invocation (closing backtick) must be gone from both Claude carriers; the
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

# 4b. run the REAL Step-4 block (the fenced block carrying the noclobber reservation) as a
#     script, in three cwds, against a throwaway state root. Main checkout and linked
#     worktree must both resolve the MAIN checkout's directory name (the arc_exit_report
#     sink); a non-git cwd must FAIL LOUD (codex r1 P2: an empty git result collapsed to "."
#     and passed the allowlist). Same-second same-title saves must reserve two DIFFERENT
#     files (codex r1 P2: append-only was a check-then-act). A title carrying $(...) is
#     sanitized to letters and never executed.
BLOCK=$(grep -l 'set -o noclobber' "$TMPD"/block*.sh 2>/dev/null | head -1)
[ -n "$BLOCK" ] || { bad "no fenced block carries the noclobber reservation"; BLOCK=/dev/null; }
STATE="$TMPD/state"
REPO="$TMPD/wsroot/slug-probe-main"; mkdir -p "$REPO"
git -C "$REPO" init -q 2>/dev/null
git -C "$REPO" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init 2>/dev/null
git -C "$REPO" worktree add -q "$TMPD/wsroot/linked-wt" -b probe-wt 2>/dev/null
run_block() { # $1=cwd $2=TITLE_RAW $3=TIMESTAMP-or-empty ; prints the block's stdout
  (cd "$1" && env GSTACK_STATE_ROOT="$STATE" TITLE_RAW="$2" TIMESTAMP="$3" bash "$BLOCK" 2>&1)
}
OUT1=$(run_block "$REPO" "probe title" ""); RC1=$?
OUT2=$(run_block "$TMPD/wsroot/linked-wt" "probe title" ""); RC2=$?
D1=$(printf '%s\n' "$OUT1" | sed -n 's/^CHECKPOINT_DIR=//p'); D2=$(printf '%s\n' "$OUT2" | sed -n 's/^CHECKPOINT_DIR=//p')
[ "$RC1" -eq 0 ] && [ "$D1" = "$STATE/projects/slug-probe-main/checkpoints" ] \
  && ok "main checkout -> projects/slug-probe-main/checkpoints" || bad "main checkout: rc=$RC1 dir='$D1'"
[ "$RC2" -eq 0 ] && [ "$D2" = "$STATE/projects/slug-probe-main/checkpoints" ] \
  && ok "linked worktree -> projects/slug-probe-main/checkpoints (not the worktree name)" || bad "worktree: rc=$RC2 dir='$D2'"
F1=$(printf '%s\n' "$OUT1" | sed -n 's/^FILE=//p')
[ -n "$F1" ] && [ -f "$F1" ] && ok "the reported FILE is reserved on disk (exclusive create)" || bad "FILE not reserved: '$F1'"
mkdir -p "$TMPD/nogit"
OUT3=$(run_block "$TMPD/nogit" "probe title" ""); RC3=$?
[ "$RC3" -ne 0 ] && printf '%s' "$OUT3" | grep -q 'FATAL: could not derive the project slug' && ! printf '%s' "$OUT3" | grep -q '^CHECKPOINT_DIR=' \
  && ok "non-git cwd fails loud (no CHECKPOINT_DIR, rc=$RC3)" || bad "non-git cwd did not fail loud: rc=$RC3 $(printf '%s' "$OUT3" | head -c 160)"
[ ! -e "$STATE/projects/./checkpoints" ] && [ ! -e "$STATE/projects/checkpoints" ] && ok "no projects/./checkpoints sink was created" || bad "a dot-slug sink was created"
OA=$(run_block "$REPO" "same title" "20990101-000000"); OB=$(run_block "$REPO" "same title" "20990101-000000")
FA=$(printf '%s\n' "$OA" | sed -n 's/^FILE=//p'); FB=$(printf '%s\n' "$OB" | sed -n 's/^FILE=//p')
[ -n "$FA" ] && [ -n "$FB" ] && [ "$FA" != "$FB" ] && [ -f "$FA" ] && [ -f "$FB" ] \
  && ok "same-second same-title saves reserve two different files" || bad "collision not resolved: '$FA' vs '$FB'"
case "$FB" in *"/20990101-000000-same-title-"????".md") ok "the loser carries a 4-char random suffix" ;; *) bad "unexpected loser name: $FB" ;; esac
OI=$(run_block "$REPO" 'ab $(touch pwned) cd' ""); FI=$(printf '%s\n' "$OI" | sed -n 's/^FILE=//p')
[ ! -e "$REPO/pwned" ] && [ ! -e "$TMPD/pwned" ] && case "$FI" in *"-ab-touch-pwned-cd.md") true ;; *) false ;; esac \
  && ok "a title with \$(...) is sanitized, never executed" || bad "injection title handled wrongly: '$FI'"

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
