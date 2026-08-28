#!/usr/bin/env bash
# Advisory textual sweep of the current diff for high-signal defect-class shapes.
# Exit contract: 0 = the sweep RAN (with or without hits); 2 = the sweep COULD NOT
# RUN (git discovery failed) — "couldn't look" must never read as "looked and found
# nothing" (codex round 4 on the skills PR). Pattern hits never affect the exit
# code: this is a collection aid for the agent's judgment, never a gate. Silence
# proves nothing; each hit demands a named answer in the preflight.
set -u
# Diff scope is a VALUE, not a mode fork: default is the authoring-time working-tree
# sweep (`git diff HEAD` + untracked files); an optional $1 names a committed range
# (`<base>..<head>`, the B-215 attest verbs) and sweeps exactly those bytes — the
# same bytes the attestation digest binds, so the sweep can never read a different
# diff than it attests. Range mode has no untracked half: content outside the range
# is outside the reviewed tree too.
range="${1:-}"
if [ -n "$range" ]; then
  if ! diff_text=$(git diff "$range" 2>&1); then
    echo "preflight-grep: SWEEP DID NOT RUN — git diff $range failed: $diff_text" >&2
    exit 2
  fi
  untracked=""
else
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
fi
added=$(printf '%s\n%s\n' "$diff_text" "$untracked" | grep '^+' | grep -v '^+++') || true
[ -z "$added" ] && { echo "preflight-grep: swept — no added lines in diff or new files"; exit 0; }

report() { # $1 label, $2 pattern
  hits=$(printf '%s\n' "$added" | grep -nE "$2" 2>/dev/null | head -8) || true
  [ -n "$hits" ] && printf '\n[%s]\n%s\n' "$1" "$hits"
}

# Same contract as report(), minus lines that already carry the exculpating token —
# the shape is only interesting when the paired handling is ABSENT (U-SR-01: the
# TimeoutExpired-without-OSError shape). The exclusion filters the matched lines and
# never the exit status: `head` terminates the pipeline either way, so an all-filtered
# result is a silent no-hit, exactly as when the first grep matches nothing.
report_unless() { # $1 label, $2 pattern, $3 exclusion
  hits=$(printf '%s\n' "$added" | grep -nE "$2" 2>/dev/null | grep -vE "$3" | head -8) || true
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
# The four U-SR-01 shapes (charter WR-03), each a mechanization of a u-he-35 finding
# the written classes alone did not fire on. Class 12's P1: a process exit code read
# as if it were the verdict, against a contract that says only the schema parse is.
report "exit code read as verdict (class 12 — name the schema parse that decides)" 'returncode +in +\(|\.returncode *(==|!=) *[0-9]'
# Spawn failure escaping the bounded call: `OSError` is what `subprocess` raises when
# the child never STARTS (missing executable, EACCES, fd exhaustion) — a child that
# starts and then dies returns a CompletedProcess carrying a negative returncode, and
# is not this shape. So a lone TimeoutExpired arm bounds only the ran-long case and
# lets the never-started one escape the very call it was meant to bound (codex r2 P3
# corrected the earlier "the child died" wording here; the eval had it right).
# Line-bound in BOTH directions, like the except/pass opener above (codex r1 P2): a
# tuple split across lines hides the pair from a line grep, so
# `except (\n subprocess.TimeoutExpired,\n ValueError,\n):` is a MISS, and
# `except (subprocess.TimeoutExpired,\n OSError):` is a false HIT whose named answer
# is "OSError is on the next line". A false hit costs one named answer; the miss is
# the real limit, and it is the tool's, not a claim this sweep can make good on —
# the file's exit contract already says silence proves nothing.
# The exclusion is anchored BEFORE any `#` (codex r3 P3): a trailing comment such as
# `except subprocess.TimeoutExpired:  # OSError still propagates` names the token
# without handling it, and a bare `OSError` exclusion would suppress the very hit that
# comment admits to earning.
report_unless "TimeoutExpired without OSError (crash aliases as timeout)" 'except[^:]*subprocess\.TimeoutExpired' '^[^#]*OSError'
# A count parsed straight off the CLI is an unvalidated budget one token from class 5:
# name the contract value that bounds it (the reps token took four paid touches).
report "argparse count without a contract-derived bound" 'type=int'
# Class 13: a new allow branch in the permission guard. The paired witness is a case
# in tools/hooks/test_permission_guard.sh — name it, or the wiring reverts green.
report "new permission-guard allow branch (name its witness)" 'elif.*printf.*TRIM.*grep +-Eq'
echo
echo "preflight-grep: done (advisory — see defect-class-preflight SKILL.md for the classes)"
exit 0
