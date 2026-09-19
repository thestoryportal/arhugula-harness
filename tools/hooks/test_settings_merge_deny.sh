#!/usr/bin/env bash
# Witness for U-HE-55 (plan §9 B1): a bare `gh pr merge` is denied by the project's
# .claude/settings.json in every permission mode. permission-guard.sh denies the same verb,
# but that guard is inert outside loop mode; this rule is what closes the interactive and
# bypass-permissions modes. The merge door (tools/hooks/safe-merge.sh) runs gh inside its own
# process, where permission rules never apply, so the rule cannot fence the door itself.
#
# settings.json is the one authority for the rules; this file pins what they must catch, not
# how they are spelled. Claude Code's matcher is modelled here, not run: a `Bash(<p>:*)` rule
# matches a command that is <p> or begins with "<p> ". What the model leaves out was probed
# live on 2026-09-19, in a bypass-permissions session with throwaway deny rules for harmless
# commands: the rule blocked the call in that mode; it also blocked its command behind
# `true &&` and behind a `FOO=1` prefix; and it was checked against both the command as
# typed and the `rtk gh ...` form the rtk PreToolUse hook rewrote it to. So the rtk rule is
# not what catches the rewrite. It catches an `rtk gh pr merge` typed directly, which the
# plain rule's prefix does not match. Section 3 checks the rewrite against the installed rtk
# and is skipped where rtk is absent (CI).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SETTINGS="$ROOT/.claude/settings.json"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

# Prints "denied" or "allowed" for one command, against the deny rules in settings.json.
# Exits non-zero (loudly) when the file is missing, unparseable, or has no deny list.
verdict() {
  python3 - "$SETTINGS" "$1" <<'PY'
import json, sys
settings, cmd = sys.argv[1], sys.argv[2]
rules = json.load(open(settings))["permissions"]["deny"]
prefixes = [r[len("Bash("):-len(":*)")] for r in rules if r.startswith("Bash(") and r.endswith(":*)")]
print("denied" if any(cmd == p or cmd.startswith(p + " ") for p in prefixes) else "allowed")
PY
}

expect() {  # <denied|allowed> <command>
  local got
  got=$(verdict "$2") || { bad "could not read the deny rules from $SETTINGS"; return; }
  [ "$got" = "$1" ] && ok "$1: $2" || bad "expected $1, got $got: $2"
}

echo "1) settings.json parses and carries a deny list"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["permissions"]["deny"]' "$SETTINGS" \
  && ok "permissions.deny present" || bad "permissions.deny missing or empty in $SETTINGS"

echo "2) every spelling of a bare merge is denied; the door and read-only gh verbs are not"
expect denied  "gh pr merge"
expect denied  "gh pr merge 1606 --squash --match-head-commit abc123"
expect denied  "rtk gh pr merge 1606 --squash"
expect allowed "tools/hooks/safe-merge.sh 1606"
expect allowed "bash tools/hooks/safe-merge.sh 1606"
expect allowed "gh pr view 1606"
expect allowed "gh pr checks 1606"
expect allowed "gh pr mergeable 1606"

echo "3) the installed rtk rewrites a bare merge to a spelling the rules deny"
if command -v rtk >/dev/null 2>&1; then
  rewritten=$(rtk hook check "gh pr merge 1606 --squash")
  [ -n "$rewritten" ] || bad "rtk hook check printed nothing"
  case "$rewritten" in
    "No rewrite"*) expect denied "gh pr merge 1606 --squash" ;;
    *) expect denied "$rewritten" ;;
  esac
else
  echo "  skip: rtk not installed"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
