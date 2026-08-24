#!/usr/bin/env bash
# Advisory textual sweep of the current diff for high-signal defect-class shapes.
# ALWAYS exits 0: this is a collection aid for the agent's judgment, never a gate
# (an advisory diagnostic that can raise is worse than none). Silence proves
# nothing; each hit demands a named answer in the preflight, not necessarily a fix.
set -u
diff_text=$(git diff HEAD 2>/dev/null; git diff --cached 2>/dev/null) || diff_text=""
added=$(printf '%s\n' "$diff_text" | grep '^+' | grep -v '^+++') || true
[ -z "$added" ] && { echo "preflight-grep: no added lines in diff"; exit 0; }

report() { # $1 label, $2 pattern
  hits=$(printf '%s\n' "$added" | grep -nE "$2" 2>/dev/null | head -8) || true
  [ -n "$hits" ] && printf '\n[%s]\n%s\n' "$1" "$hits"
}

report "silent-failure shapes"        '2>/dev/null|\|\| true|except[^:]*: *pass'
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
