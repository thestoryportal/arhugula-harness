#!/usr/bin/env bash
# Advisory textual sweep of the current diff for high-signal defect-class shapes.
# Exit contract: 0 = the sweep RAN (with or without hits); 2 = the sweep COULD NOT
# RUN (git discovery failed) — "couldn't look" must never read as "looked and found
# nothing" (codex round 4 on the skills PR). Pattern hits never affect the exit
# code: this is a collection aid for the agent's judgment, never a gate. Silence
# proves nothing; each hit demands a named answer in the preflight.
set -u
# `git diff HEAD` already covers staged + unstaged changes to tracked files —
# concatenating `--cached` on top duplicated staged hits and let them eat the
# per-class head cap (codex round 1). Untracked NEW files are outside any diff,
# so their content is appended as +lines to honor the SKILL's "plus any new
# files" scope.
if ! diff_text=$(git diff HEAD 2>&1); then
  echo "preflight-grep: SWEEP DID NOT RUN — git diff HEAD failed: $diff_text" >&2
  exit 2
fi
if ! untracked_list=$(git ls-files --others --exclude-standard 2>&1); then
  echo "preflight-grep: SWEEP DID NOT RUN — git ls-files failed: $untracked_list" >&2
  exit 2
fi
untracked=$(printf '%s\n' "$untracked_list" | while IFS= read -r f; do
  [ -f "$f" ] && sed 's/^/+/' "$f"
done) || untracked=""
added=$(printf '%s\n%s\n' "$diff_text" "$untracked" | grep '^+' | grep -v '^+++') || true
[ -z "$added" ] && { echo "preflight-grep: swept — no added lines in diff or new files"; exit 0; }

report() { # $1 label, $2 pattern
  hits=$(printf '%s\n' "$added" | grep -nE "$2" 2>/dev/null | head -8) || true
  [ -n "$hits" ] && printf '\n[%s]\n%s\n' "$1" "$hits"
}

# Two silent-failure patterns: the one-liner form, and the except-line-with-empty-
# suffix that opens the standard MULTILINE `except ...:\n    pass` (a line-based
# grep cannot span lines, so the opener is the flaggable half — codex round 1).
report "silent-failure shapes"        '2>/dev/null|\|\| true|except[^:]*: *pass'
report "except-block opener (check its body for pass/swallow)" 'except[^:]*: *$'
report "env writes outside MonkeyPatch" 'os\.environ\[[^]]+\] *='
# The hand-rolled save/restore pair was named in only 1 of 4 skill-eval review runs
# despite being in the checklist — class 6 demoted to a mechanical pattern (the
# activation-ladder rule): flag BOTH halves so the pair is unmissable.
report "save/restore pair: capture half" '(saved|prev|old|prior)\w* *= *os\.environ\.get'
report "save/restore pair: two-armed restore" 'if +\w+ +is +None: *$|\.pop\([^)]*None\)|del +os\.environ'
report "check-then-act on paths"      '\.exists\(\)|os\.path\.exists|isfile\('
report "sleeps in tests"              'time\.sleep|sleep [0-9]'
report "bare counts/absolutes in prose" '(^\+.*(#|"""|\*).*(all |every |only |exactly [0-9]+|[0-9]+ (witnesses|rows|files|tests)))'
report "new retry/timeout constants"  'timeout|retry|deadline|budget'
echo
echo "preflight-grep: done (advisory — see defect-class-preflight SKILL.md for the ten classes)"
exit 0
