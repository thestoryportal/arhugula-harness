#!/usr/bin/env bash
# Witness for U-SR-09 b4 (plan §8 R2): the rtk grep-rewrite shape guard.
#
# Sections 1-3 are hermetic: a STUB `rtk` on PATH answers `hook check` the way rtk 0.40.0
# does (prints `rtk grep …` when the command-position word is grep/rg, else "No rewrite
# for: …") and records every invocation, so the guard's plumbing -- pre-check, oracle,
# shape judgement, correction, deny JSON, silence -- is exercised in CI where rtk is absent.
# Section 4 runs only where the REAL rtk is installed and is the guard's EXIT PLAN: it
# asserts each guarded shape still fails under `rtk grep` and works under `rtk proxy`; the
# day a newer rtk translates them correctly it reds with the instruction to delete the guard.
#
# The hook runs IN PLACE (bash "$SCRIPT_DIR/<hook>"; copying it out breaks its lib.sh
# source and it exits 0 silently -- a vacuous green), with CLAUDE_PROJECT_DIR pointed at a
# throwaway dir and HARNESS_CODEX_REVIEW_ISOLATED unset (hooks early-exit on it).

# mutation-probe: tools/hooks/rtk-shape-guard.sh:92-93 the deny emission (drop it -> no deny -> section 2 reds; the shape judgement itself is probed via tools/test_rtk_shape_guard.py)

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$SCRIPT_DIR/rtk-shape-guard.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
OUT="$REPO/out.txt"
STUBDIR="$REPO/stubbin"; mkdir -p "$STUBDIR"
CALLS="$REPO/rtk-calls.log"

# The stub: rtk 0.40.0's dry-run shape, witnessed at U-SR-09 -- `grep`/`rg` at a command
# position (start, after `;`/`&&`) becomes `rtk grep`; a pipeline's SECOND command and every
# other word are untouched ("rtk ls | grep …"); egrep / git grep / rtk proxy are never rewritten.
cat > "$STUBDIR/rtk" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "${RTK_STUB_CALLS:?}"
[ "$1" = hook ] && [ "$2" = check ] || { echo "stub: unsupported $*" >&2; exit 2; }
shift 2; cmd="$*"
out=$(printf '%s' "$cmd" | sed -E 's/(^[[:space:]]*|[;&][[:space:]]*)(grep|rg)([[:space:]])/\1rtk grep\3/g')
# rtk 0.40.0 sometimes echoes an unrewritten command back verbatim instead of "No rewrite
# for:" (both forms seen at U-SR-09); RTK_STUB_ECHO=1 reproduces the echo form.
if [ "$out" = "$cmd" ] && [ -n "${RTK_STUB_ECHO:-}" ]; then echo "$cmd"; exit 0; fi
if [ "$out" = "$cmd" ]; then echo "No rewrite for: $cmd"; else echo "$out"; fi
EOF
chmod +x "$STUBDIR/rtk"

# payload <cmd>: the PreToolUse JSON for a Bash command, JSON-escaped by python (the shapes
# under test carry backslashes and quotes a printf template would corrupt), written to a
# file and fed on stdin by redirection -- never a pipe: a hook that exits before reading
# stdin would EPIPE the writer, and under pipefail that status masks the hook's own.
PAYLOAD="$REPO/payload.json"
payload() { python3 -c 'import json,sys; print(json.dumps({"session_id":"probe","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1" > "$PAYLOAD"; }
# The guard fires only where rtk's rewrite hook is REGISTERED (Claude user settings); the
# fixture registers it under a throwaway CLAUDE_CONFIG_DIR, and one case below omits it.
CFG="$REPO/claude-config"; mkdir -p "$CFG"
printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"rtk hook claude"}]}]}}\n' > "$CFG/settings.json"
NOCFG="$REPO/claude-config-none"; mkdir -p "$NOCFG"
printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"echo other"}]}]}}\n' > "$NOCFG/settings.json"
# run_guard <bash-command>: PATH = stub first; stdout+stderr -> $OUT; echoes the exit code.
run_guard() {
  payload "$1"
  env -u HARNESS_CODEX_REVIEW_ISOLATED PATH="$STUBDIR:$PATH" RTK_STUB_CALLS="$CALLS" CLAUDE_CONFIG_DIR="$CFG" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" < "$PAYLOAD" > "$OUT" 2>&1
  echo $?
}
bytes() { wc -c < "$OUT" | tr -d ' '; }
calls() { [ -f "$CALLS" ] && wc -l < "$CALLS" | tr -d ' ' || echo 0; }
# deny_reason: the output is exactly one closed PreToolUse deny decision; prints its reason.
deny_reason() { python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
h = d["hookSpecificOutput"]
assert set(d) == {"hookSpecificOutput"}, d
assert set(h) == {"hookEventName", "permissionDecision", "permissionDecisionReason"}, h
assert h["hookEventName"] == "PreToolUse" and h["permissionDecision"] == "deny", h
print(h["permissionDecisionReason"])
' "$1" 2>/dev/null; }

expect_silent() { # <label> <cmd>
  rc=$(run_guard "$2"); b=$(bytes)
  [ "$rc" -eq 0 ] && [ "$b" -eq 0 ] && ok "$1: '$2' -> exit 0, 0 bytes" || bad "$1: '$2' -> exit $rc, $b bytes: $(head -c 300 "$OUT")"
}
expect_deny() { # <label> <cmd> <expected re-issue substring> <expected shape word>
  rc=$(run_guard "$2")
  reason=$(deny_reason "$OUT") || { bad "$1: '$2' -> not a closed deny decision (rc=$rc): $(head -c 300 "$OUT")"; return; }
  case "$reason" in
    *"Re-issue as: $3"*) ok "$1: '$2' -> deny with re-issue '$3'" ;;
    *) bad "$1: '$2' -> deny but re-issue missing '$3': $reason" ;;
  esac
  case "$reason" in *"$4"*) ok "$1: reason names the shape ($4)" ;; *) bad "$1: reason does not name '$4': $reason" ;; esac
}

# --- 1. silence: plain commands, clean rewrites, escape flags, pipeline greps --------------
: > "$CALLS"
expect_silent "plain non-grep" 'ls -la /tmp'
[ "$(calls)" -eq 0 ] && ok "pre-check: the oracle is never spawned for a non-grep command" || bad "oracle spawned $(calls)x for 'ls -la /tmp'"
expect_silent "clean rewrite" 'grep -n foo file.txt'
[ "$(calls)" -eq 1 ] && ok "oracle consulted exactly once for a grep command" || bad "oracle calls after one grep: $(calls)"
expect_silent "alternation alone (round-trips on 0.40.0 -- NOT guarded)" 'grep -n "a\|b" file.txt'
expect_silent "-E makes the paren a group on both sides" 'grep -nE "f(x)" file.txt'
expect_silent "-F makes the paren literal on both sides" 'grep -F "f(" file.txt'
expect_silent "-P" 'grep -P "f(x)" file.txt'
expect_silent "combined short flags carry the escape" 'grep -rnE "f(" tools'
expect_silent "escaped paren is a BRE group, not a hard failure (out of scope)" 'grep -n "f\(x\)" file.txt'
expect_silent "pipeline grep is not rewritten by rtk" 'ls | grep "f(" '
expect_silent "egrep is not rewritten by rtk" 'egrep "f(x)" file.txt'
expect_silent "rtk proxy is left alone" 'rtk proxy grep -n "f(" file.txt'
expect_silent "rtk proxy rg --glob is left alone" 'rtk proxy rg --glob "*.py" main tools'
# codex u-sr-09 r7: the words `rtk grep` INSIDE an unrewritten command are not a rewrite --
# neither under the "No rewrite for:" form nor the verbatim-echo form of the dry-run
expect_silent "'No rewrite for:' echo carrying the words rtk grep" "echo rtk grep 'f('"
payload "echo rtk grep 'f('"
env -u HARNESS_CODEX_REVIEW_ISOLATED PATH="$STUBDIR:$PATH" RTK_STUB_CALLS="$CALLS" RTK_STUB_ECHO=1 CLAUDE_CONFIG_DIR="$CFG" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" < "$PAYLOAD" > "$OUT" 2>&1; rc=$?
[ "$rc" -eq 0 ] && [ "$(bytes)" -eq 0 ] && ok "verbatim-echo form carrying the words rtk grep -> exit 0, 0 bytes" || bad "verbatim echo denied: rc=$rc $(head -c 200 "$OUT")"

# --- 2. the two guarded shapes, with the exact re-issue ----------------------------------
expect_deny "--glob" 'rg --glob "*.py" "def main" tools' 'rtk proxy rg --glob "*.py" "def main" tools' '--glob/-g'
expect_deny "-g short form" 'rg -g "*.py" main tools' 'rtk proxy rg -g "*.py" main tools' '--glob/-g'
expect_deny "bare paren" 'grep -rn "hook_emit(" tools/hooks' 'rtk proxy grep -rn "hook_emit(" tools/hooks' 'unescaped paren'
expect_deny "closing paren" 'grep -n "x)" f.txt' 'rtk proxy grep -n "x)" f.txt' 'unescaped paren'
expect_deny "alternation + paren (the [B] parse-error shape)" 'grep -n "a\|f(" f.txt' 'rtk proxy grep -n "a\|f(" f.txt' 'unescaped paren'
# a compound command is NEVER re-joined (codex r3/r4: redirections and globs would not survive a
# token re-join) -- the deny still fires, with "re-issue by hand"; a single simple command is
# prefixed VERBATIM (the cases above)
expect_deny_by_hand() { # <label> <cmd>
  rc=$(run_guard "$2")
  reason=$(deny_reason "$OUT") || { bad "$1: '$2' -> not a closed deny decision (rc=$rc): $(head -c 300 "$OUT")"; return; }
  case "$reason" in
    *"Re-issue by hand"*) ok "$1: '$2' -> deny, re-issue by hand (never a fabricated compound command)" ;;
    *) bad "$1: '$2' -> deny but no by-hand instruction: $reason" ;;
  esac
}
expect_deny_by_hand "after ; no re-join is offered" 'cd /tmp; grep -n "f(" *.py'
expect_deny_by_hand "before && no re-join is offered" 'grep -n "f(" f && echo ok'
rc=$(run_guard 'rg -g "*.py" "f(" tools'); reason=$(deny_reason "$OUT")
# codex r6: only the ORIGINAL executable's shape is a rewrite defect -- an rg original is
# denied for the glob alone (rg chokes on the paren natively), a grep original for the paren
# alone (grep never had -g)
case "$reason" in *'--glob/-g'*'unescaped paren'*) bad "rg original: the paren is rg's own failure, not the rewrite's: $reason" ;; *'--glob/-g'*) ok "rg original with both shapes: glob named, paren not (rg fails on it natively)" ;; *) bad "rg original: glob expected: $reason" ;; esac
rc=$(run_guard 'grep -g "*.py" "f(" tools'); reason=$(deny_reason "$OUT")
case "$reason" in *'--glob/-g'*) bad "grep original: -g never worked on grep, not a rewrite defect: $reason" ;; *'unescaped paren'*) ok "grep original with both shapes: paren named, glob not (grep never had -g)" ;; *) bad "grep original: paren expected: $reason" ;; esac
expect_silent "rg original with only a paren (fails on rg natively; no remedy helps)" 'rg "f(" x'
expect_silent "grep original with only -g (never worked on grep)" 'grep -g "*.py" x'
# codex u-sr-09 r1 (three P2s on the sed-based first cut): quote-aware end to end
expect_deny "quoted && inside the pattern is not a separator" "grep -n 'a && f(' file" "rtk proxy grep -n 'a && f(' file" 'unescaped paren'
expect_deny "attached -g value" "rg -g'*.py' needle tree" "rtk proxy rg -g'*.py' needle tree" '--glob/-g'
expect_deny "quoted '; grep literal' argument is left alone in the re-issue" "rg -g '*.py' needle '; grep literal'" "rtk proxy rg -g '*.py' needle '; grep literal'" '--glob/-g'
expect_silent "a quoted separator word as the pattern is a word" "grep '|' file.txt"

# --- 2b. registration (codex u-sr-09 r1 P3): settings.json runs this guard on Bash -----------
python3 - "$ROOT/.claude/settings.json" <<'EOF' && ok "settings.json: a PreToolUse Bash group runs rtk-shape-guard.sh" || bad "settings.json no longer registers rtk-shape-guard.sh on PreToolUse Bash"
import json, sys
d = json.load(open(sys.argv[1]))["hooks"]
hits = [row.get("matcher") for row in d.get("PreToolUse", []) for h in row.get("hooks", []) if h.get("command", "").endswith("/tools/hooks/rtk-shape-guard.sh")]
sys.exit(0 if any(m in (None, "", "*", "Bash") or "Bash" in str(m).split("|") for m in hits) else 1)
EOF
# rtk's rewrite hook NOT registered for the venue -> silent even on a guarded shape
payload 'grep -rn "hook_emit(" tools/hooks'
env -u HARNESS_CODEX_REVIEW_ISOLATED PATH="$STUBDIR:$PATH" RTK_STUB_CALLS="$CALLS" CLAUDE_CONFIG_DIR="$NOCFG" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" < "$PAYLOAD" > "$OUT" 2>&1; rc=$?
[ "$rc" -eq 0 ] && [ "$(bytes)" -eq 0 ] && ok "rtk hook not registered in the venue's settings -> exit 0, 0 bytes" || bad "unregistered venue -> rc=$rc $(bytes) bytes: $(head -c 200 "$OUT")"
env -u HARNESS_CODEX_REVIEW_ISOLATED PATH="$STUBDIR:$PATH" RTK_STUB_CALLS="$CALLS" CLAUDE_CONFIG_DIR="$REPO/no-such-dir" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" < "$PAYLOAD" > "$OUT" 2>&1; rc=$?
[ "$rc" -eq 0 ] && [ "$(bytes)" -eq 0 ] && ok "no settings file at all -> exit 0, 0 bytes" || bad "missing settings -> rc=$rc $(bytes) bytes"

# --- 3. no rtk on PATH / review-isolated -> silent even on a guarded shape ----------------
# "rtk absent" = the caller's PATH minus every directory that holds an rtk (the stub's and
# the real one's), so jq/sed/grep stay reachable and only the oracle binary is gone.
NORTK_PATH=$(python3 -c 'import os,sys; print(":".join(d for d in os.environ["PATH"].split(":") if d and not os.access(os.path.join(d,"rtk"), os.X_OK)))')
if env PATH="$NORTK_PATH" bash -c 'command -v rtk' >/dev/null 2>&1; then
  bad "could not build an rtk-free PATH (rtk still resolves): $NORTK_PATH"
else
  payload 'grep -rn "hook_emit(" tools/hooks'
  env -u HARNESS_CODEX_REVIEW_ISOLATED PATH="$NORTK_PATH" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" < "$PAYLOAD" > "$OUT" 2>&1; rc=$?
  [ "$rc" -eq 0 ] && [ "$(bytes)" -eq 0 ] && ok "rtk absent -> exit 0, 0 bytes (nothing rewrites, nothing to guard)" || bad "rtk absent -> rc=$rc $(bytes) bytes: $(head -c 200 "$OUT")"
fi
payload 'grep -rn "hook_emit(" tools/hooks'
env HARNESS_CODEX_REVIEW_ISOLATED=1 PATH="$STUBDIR:$PATH" RTK_STUB_CALLS="$CALLS" CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK" < "$PAYLOAD" > "$OUT" 2>&1; rc=$?
[ "$rc" -eq 0 ] && [ "$(bytes)" -eq 0 ] && ok "review-isolated -> exit 0, 0 bytes" || bad "review-isolated -> rc=$rc $(bytes) bytes"

# --- 4. EXIT PLAN -- the real rtk (presence-gated, stated loudly) ---------------------------
# Each guarded shape must STILL fail under `rtk grep` and work under `rtk proxy`; `\|` alone
# must still round-trip (the reason it is not guarded). A flip here means rtk changed: on a
# fix, delete rtk-shape-guard.sh + this test + the lanes_verify row + the settings entry.
if command -v rtk >/dev/null 2>&1 && command -v rg >/dev/null 2>&1; then
  echo "  rtk present: $(rtk --version 2>&1 | head -1)"
  FX="$REPO/fx/sub"; mkdir -p "$FX"; printf 'alpha\nbeta\nf(x)\n' > "$FX/f.txt"
  ( cd "$REPO/fx" && rtk grep --glob "*.txt" alpha sub >/dev/null 2>&1 ); rc_bad=$?
  ( cd "$REPO/fx" && rtk proxy rg --glob "*.txt" alpha sub >/dev/null 2>&1 ); rc_good=$?
  [ "$rc_bad" -ne 0 ] && [ "$rc_good" -eq 0 ] && ok "real rtk: --glob still fails under rtk grep (rc=$rc_bad) and works under rtk proxy" \
    || bad "real rtk: --glob shape changed (rtk grep rc=$rc_bad, rtk proxy rc=$rc_good) -- rtk fixed this: DELETE the guard"
  ( cd "$REPO/fx" && rtk grep -n "f(" sub/f.txt >/dev/null 2>&1 ); rc_bad=$?
  good=$(cd "$REPO/fx" && rtk proxy grep -n "f(" sub/f.txt 2>/dev/null)
  [ "$rc_bad" -ne 0 ] && [ "$good" = "3:f(x)" ] && ok "real rtk: bare paren still fails under rtk grep (rc=$rc_bad) and works under rtk proxy" \
    || bad "real rtk: paren shape changed (rtk grep rc=$rc_bad, rtk proxy '$good') -- rtk fixed this: DELETE the guard"
  alt=$(cd "$REPO/fx" && rtk grep -n "alpha\|beta" sub/f.txt 2>/dev/null)
  case "$alt" in *alpha*beta*) ok "real rtk: \\| alone still round-trips (the reason it is not guarded)" ;; *) bad "real rtk: \\| alone no longer round-trips: '$alt' -- add it to the guard" ;; esac
  # the re-issue shape through rtk's REAL hook (the dry-run's print form varies; the JSON
  # hook is the mechanism): zero bytes = no rewrite.
  payload 'rtk proxy grep -n "f(" x'
  chk=$(rtk hook claude < "$PAYLOAD" 2>/dev/null | wc -c | tr -d ' ')
  [ "$chk" -eq 0 ] && ok "real rtk: the re-issue shape is not re-rewritten (0 bytes from rtk hook claude)" || bad "real rtk re-rewrites 'rtk proxy grep' ($chk bytes)"
else
  echo "  rtk or rg absent: section 4 (exit-plan witness on the real binary) NOT run -- recorded on the U-SR-09 PR"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
