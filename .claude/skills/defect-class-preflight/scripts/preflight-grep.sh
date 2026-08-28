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
# Only the charter's shape, `returncode in (`. A `.returncode == / != N` alternative was
# tried and REMOVED (codex r6 P2): `proc.returncode != 0` is the ordinary way to check a
# child's status, so it fired on correct code — and with report()'s eight-hit cap, eight
# such false positives can push a real verdict misuse out of the report while the
# attestation still shows the label answered. A detector whose noise can hide its own
# signal is worse than a narrower one.
report "exit code read as verdict (class 12 — name the schema parse that decides)" 'returncode +in +\('
# Spawn failure escaping a bounded call. `OSError` is what `subprocess` raises when the
# child never STARTS (missing executable, EACCES, fd exhaustion); a child that starts
# and then dies returns a CompletedProcess with a negative returncode and is NOT this
# shape. So a lone TimeoutExpired arm bounds only the ran-long case and lets the
# never-started one escape the call it was meant to bound.
#   Match: any `TimeoutExpired`, qualified or bare — `from subprocess import
#   TimeoutExpired` is the same defect, and demanding the dotted spelling let preflight
#   attest the intended shape as having no hit.
#   Exclude: only OSError inside the except CLAUSE (`except[^:]*OSError`), so a mention
#   in a trailing comment or a statement after the colon never counts as handling.
#   Bound, not fixed: this is line-based. A tuple split across lines is a MISS, and
#   `except (subprocess.TimeoutExpired,\n OSError):` is a false HIT whose named answer
#   is "OSError is on the next line". A false hit costs one named answer; the miss is
#   the tool's limit, and the exit contract above already says silence proves nothing.
report_unless "TimeoutExpired without OSError (crash aliases as timeout)" 'except[^:]*\bTimeoutExpired' 'except[^:]*\bOSError\b'
# A count parsed straight off the CLI is an unvalidated budget one token from class 5:
# name the contract value that bounds it (the reps token took four paid touches).
# Deliberately the bare charter shape, not `add_argument[^)]*type=int`. That scoping was
# tried and REVERTED (codex r10 P2): `add_argument(` and `type=int` sit on different lines
# in the ordinary multiline call — tools/mutation_probe.py:1601-1603 is one — so a
# line-based grep scoped that way misses the common case entirely.
# NOTE the direction, because it is the OPPOSITE of refresh-classes.py's: there, a false
# match silently drops a row from new-class discovery, so that table prefers to MISS. Here
# a miss means the defect ships, while a false hit costs exactly one named answer in the
# preflight. This sweep therefore prefers to OVER-match. Same author, same arc, opposite
# safe direction — the tool's failure mode decides, not a house style.
report "argparse count without a contract-derived bound" 'type=int'
# Class 13: a new allow branch in the permission guard. The paired witness is a case
# in tools/hooks/test_permission_guard.sh — name it, or the wiring reverts green.
report "new permission-guard allow branch (name its witness)" 'elif.*printf.*TRIM.*grep +-Eq'
echo
echo "preflight-grep: done (advisory — see defect-class-preflight SKILL.md for the classes)"
exit 0
