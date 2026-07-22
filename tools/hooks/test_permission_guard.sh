#!/usr/bin/env bash
# Hermetic test for permission-guard.sh (U-HK-12). Synthetic PreToolUse/PermissionRequest
# payloads against a throwaway project dir. Asserts the tri-state: inert off-mode,
# deny-list (force-push, rm -rf, secret reloc, paid MCP), allowlist (safe bash, Read,
# Edit), design-substrate Edit → ask, unknown → ask, and the PermissionRequest schema.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/permission-guard.sh"

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL mktemp"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
mkdir -p "$REPO/.harness"

# Helpers: build a payload + run the hook with loop mode forced via env.
pl() { # $1=tool $2=command $3=file_path $4=event
  jq -nc --arg t "$1" --arg c "$2" --arg f "$3" --arg e "${4:-PreToolUse}" \
    '{"hook_event_name":$e,"tool_name":$t,"tool_input":{"command":$c,"file_path":$f}}'
}
run_on()  { printf '%s' "$1" | HARNESS_LOOP=1 CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }   # loop ON
run_off() { printf '%s' "$1" | CLAUDE_PROJECT_DIR="$REPO" bash "$HOOK"; }                   # loop OFF (unset)
dec()  { echo "$1" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null; }
beh()  { echo "$1" | jq -r '.hookSpecificOutput.decision.behavior // empty' 2>/dev/null; }

unset HARNESS_LOOP

# 1) INERT when loop mode off — even a force-push must produce NO output.
OUT=$(run_off "$(pl Bash 'git push --force origin main' '')")
[ -z "$OUT" ] && ok "inert when loop mode off" || bad "produced output off-mode: $OUT"

# 2) DENY-LIST (loop on).
OUT=$(run_on "$(pl Bash 'git push --force origin main' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny force-push" || bad "force-push not denied: $OUT"
OUT=$(run_on "$(pl Bash 'rm -rf build/' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny rm -rf" || bad "rm -rf not denied: $OUT"
OUT=$(run_on "$(pl Bash 'git reset --hard origin/main' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny git reset --hard" || bad "reset --hard not denied: $OUT"
OUT=$(run_on "$(pl Bash 'cp .env /tmp/backup.env' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny secret relocation" || bad "secret reloc not denied: $OUT"
OUT=$(run_on "$(pl Bash 'gh secret set FOO' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny gh secret" || bad "gh secret not denied: $OUT"
OUT=$(run_on "$(pl Bash 'curl https://api.anthropic.com/v1/messages' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny paid provider call" || bad "provider call not denied: $OUT"
OUT=$(run_on "$(pl mcp__harness-7a-scaffold__route_llm_call '' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "deny paid MCP route_llm_call" || bad "paid MCP not denied: $OUT"

# 3) DENY is logged to the ledger.
grep -q '| DENY |' "$REPO/.harness/loop_status.md" && ok "deny logged to ledger" || bad "deny not logged"

# 4) ALLOWLIST.
OUT=$(run_on "$(pl Bash 'git status' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow git status" || bad "git status not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'git commit -m wip' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow git commit" || bad "git commit not allowed: $OUT"

# 4b) Loop-control wrappers (U-HK-14/15) — the P1 regression. The defer-and-continue
#     mechanism's RECORD step must be runnable in loop mode REGARDLESS of args, including a
#     deferral REASON mentioning credentials/secret (the wrapper only appends a ledger row;
#     it bypasses _bash_args_safe). If denied, the headless skip-set never populates and the
#     loop re-attempts the same gated item every iteration. A raw chained `source … &&
#     loop_defer …` (malformed + denied) must still NOT auto-allow.
OUT=$(run_on "$(pl Bash "tools/04-loop/defer.sh R-300 'needs OpenAI credentials — built without it: mock fixture'" '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow defer.sh wrapper (even with 'credentials' in the reason)" || bad "defer.sh not allowed: $OUT"
OUT=$(run_on "$(pl Bash "bash tools/04-loop/defer.sh R-410 'needs container runtime'" '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow 'bash tools/04-loop/defer.sh ...'" || bad "bash defer.sh not allowed: $OUT"
OUT=$(run_on "$(pl Bash "tools/04-loop/resolve.sh R-410 'ratified via council dyad — see PR #1234'" '')")
[ -z "$(dec "$OUT")" ] && ok "resolve.sh NOT auto-allowed (falls to ask — resolution needs a human present, unlike defer/halt)" || bad "resolve.sh wrongly auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash "bash tools/04-loop/resolve.sh R-410 'operator ran gh secret set to unblock this'" '')")
[ "$(dec "$OUT")" = "deny" ] && ok "resolve.sh with a 'gh secret set' note hits the deny-list (no bypass exemption)" || bad "resolve.sh credential note not denied: $OUT"
OUT=$(run_on "$(pl Bash "tools/04-loop/halt.sh 'forward menu exhausted — 3 awaiting input'" '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow halt.sh wrapper (stand-down)" || bad "halt.sh not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'source tools/hooks/lib.sh && loop_defer R-1 x' '')")
[ -z "$(dec "$OUT")" ] && ok "chained source+loop_defer NOT auto-allowed (falls to ask — the denied/malformed original)" || bad "chained source auto-allowed: $OUT"
# 4c) Wrapper with an env-var expansion must NOT auto-allow (the shell would expand the
#     secret VALUE into the ledger). Literal "credentials" is fine (4b); `$VAR` is not.
OUT=$(run_on "$(pl Bash 'tools/04-loop/defer.sh R-300 $OPENAI_API_KEY' '')")
[ -z "$(dec "$OUT")" ] && ok "defer.sh with \$VAR expansion NOT auto-allowed (no secret leak)" || bad "defer.sh \$VAR auto-allowed (secret-leak vector): $OUT"
OUT=$(run_on "$(pl Bash 'tools/04-loop/resolve.sh R-300 $OPENAI_API_KEY' '')")
[ -z "$(dec "$OUT")" ] && ok "resolve.sh with \$VAR expansion NOT auto-allowed (no secret leak)" || bad "resolve.sh \$VAR auto-allowed (secret-leak vector): $OUT"
# 4d) A deferral REASON that names an operator action (gh secret / .env) must ALLOW — the
#     wrapper short-circuits BEFORE the free-text deny scan, else the deferral is denied,
#     no ledger row is written, and the headless loop retries the gated item to the cap.
OUT=$(run_on "$(pl Bash "tools/04-loop/defer.sh R-300 'operator must run gh secret set OPENAI_API_KEY'" '')")
[ "$(dec "$OUT")" = "allow" ] && ok "defer.sh reason naming 'gh secret' ALLOWED (deny-scan exempt)" || bad "defer.sh reason tripped deny-list: $OUT"
# 4e) ...but a real `gh secret set` command (not the wrapper) is STILL hard-stopped, and a
#     wrapper with a chained dangerous follow-on is STILL denied (control-op stops the
#     short-circuit → falls through to the deny-list).
OUT=$(run_on "$(pl Bash 'gh secret set FOO' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "real 'gh secret set' still denied (short-circuit is wrapper-only)" || bad "gh secret leaked through: $OUT"
OUT=$(run_on "$(pl Bash 'tools/04-loop/defer.sh R-1 x; rm -rf /' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "wrapper + chained 'rm -rf' still denied (control-op → deny-list)" || bad "chained rm-rf via wrapper not denied: $OUT"
OUT=$(run_on "$(pl Bash 'tools/04-loop/resolve.sh R-1 x; rm -rf /' '')")
[ "$(dec "$OUT")" = "deny" ] && ok "resolve.sh + chained 'rm -rf' still denied (control-op → deny-list)" || bad "chained rm-rf via resolve.sh not denied: $OUT"
OUT=$(run_on "$(pl Bash 'bash tools/hooks/test_loop_lib.sh' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow hermetic test run" || bad "test run not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'gh pr create --fill' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "allow gh pr create" || bad "gh pr not allowed: $OUT"
OUT=$(run_on "$(pl Read '' "$REPO/src/y.py")")
[ "$(dec "$OUT")" = "allow" ] && ok "allow in-worktree Read" || bad "in-worktree Read not allowed: $OUT"
OUT=$(run_on "$(pl Edit '' "$REPO/tools/hooks/foo.sh")")
[ "$(dec "$OUT")" = "allow" ] && ok "allow Edit to normal path" || bad "Edit not allowed: $OUT"

# 5) ASK (no output) — design-substrate Edit + unknown bash + bare git push (non-force).
OUT=$(run_on "$(pl Edit '' '/repo/design-substrate/Spec_X.md')")
[ -z "$OUT" ] && ok "design-substrate Edit → ask (no auto-approve)" || bad "design-substrate auto-decided: $OUT"
# 5b) loop_status.md Edit/Write → ask (codex [P1] round 4: excluding resolve.sh from the
#     Bash short-circuit does nothing if a plain Edit/Write to the ledger is still
#     auto-allowed — an unattended agent could append a fabricated RESOLVED-HIL row
#     directly, bypassing the resolve.sh gate entirely).
OUT=$(run_on "$(pl Edit '' "$REPO/.harness/loop_status.md")")
[ -z "$OUT" ] && ok "loop_status.md Edit → ask (no auto-approve; ledger is audit-only)" || bad "loop_status.md Edit auto-decided: $OUT"
OUT=$(run_on "$(pl Write '' "$REPO/.harness/loop_status.md")")
[ -z "$OUT" ] && ok "loop_status.md Write → ask (no auto-approve)" || bad "loop_status.md Write auto-decided: $OUT"
OUT=$(run_on "$(pl Edit '' '.harness/loop_status.md')")
[ -z "$OUT" ] && ok "loop_status.md Edit (relative path) → ask" || bad "loop_status.md relative Edit auto-decided: $OUT"
OUT=$(run_on "$(pl Bash 'python scripts/migrate.py --wipe' '')")
[ -z "$OUT" ] && ok "unknown bash → ask" || bad "unknown bash auto-decided: $OUT"

# 5b) CHAINED/NESTED command with a safe PREFIX must NOT auto-allow (codex P1). A safe
#     prefix fronting a dangerous follow-on falls through to ask.
OUT=$(run_on "$(pl Bash 'git status && python scripts/migrate.py --wipe' '')")
[ -z "$OUT" ] && ok "safe-prefix && danger → ask (no chained auto-allow)" || bad "chained cmd auto-decided: $OUT"
OUT=$(run_on "$(pl Bash 'uv run python scripts/migrate.py --wipe' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "uv run python wipe → not auto-allowed" || bad "uv-run-python auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'cat secrets.txt | sh' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "piped cat | sh → not auto-allowed" || bad "pipe auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'git log $(rm -rf /)' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "command substitution → not auto-allowed" || bad "cmd-subst auto-allowed: $OUT"

# 5c) Edit/Write to a secret file must NOT auto-allow (codex P1) — falls through to ask.
OUT=$(run_on "$(pl Edit '' "$REPO/.env")")
[ -z "$OUT" ] && ok ".env Edit → ask (no auto-approve)" || bad ".env edit auto-decided: $OUT"
OUT=$(run_on "$(pl Write '' "$REPO/config/credentials.json")")
[ -z "$OUT" ] && ok "credentials Write → ask" || bad "credentials write auto-decided: $OUT"
OUT=$(run_on "$(pl Write '' '/home/u/.ssh/id_rsa')")
[ -z "$OUT" ] && ok "id_rsa Write → ask" || bad "id_rsa write auto-decided: $OUT"

# 5d) Edit OUTSIDE the worktree / into .git / via traversal must NOT auto-allow (codex P1).
OUT=$(run_on "$(pl Edit '' "$HOME/.claude/settings.json")")
[ -z "$OUT" ] && ok "edit outside worktree → ask" || bad "outside-worktree edit auto-decided: $OUT"
OUT=$(run_on "$(pl Write '' "$REPO/.git/config")")
[ -z "$OUT" ] && ok "edit into .git → ask" || bad ".git edit auto-decided: $OUT"
OUT=$(run_on "$(pl Edit '' "$REPO/../escape.txt")")
[ -z "$OUT" ] && ok "path traversal → ask" || bad "traversal edit auto-decided: $OUT"
OUT=$(run_on "$(pl Edit '' "$REPO/src/mod.py")")
[ "$(dec "$OUT")" = "allow" ] && ok "in-worktree edit → allow" || bad "in-worktree edit not allowed: $OUT"

# 5e) Destructive SUBMODES of allowlisted verbs must NOT auto-allow (codex P1).
OUT=$(run_on "$(pl Bash 'find . -name node_modules -delete' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "find -delete → not auto-allowed" || bad "find -delete auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'gh api -X DELETE repos/o/r/issues/1' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "gh api -X DELETE → not auto-allowed" || bad "gh api delete auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'uv run python wipe.py' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "uv run python → not auto-allowed" || bad "uv-run-python auto-allowed: $OUT"
# content-reader / programmable-filter verbs are NOT auto-allowed (arg safety unvalidatable)
OUT=$(run_on "$(pl Bash 'find . -name *.py' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "find → ask (content verbs dropped)" || bad "find auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'gh api repos/o/r' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "gh api GET → allow" || bad "gh api GET not allowed: $OUT"

# 5f) Workspace-DISCARDING git commands must NOT auto-allow (codex P1) — they can erase
#     uncommitted work and the deny-list only catches reset/rebase/force-push.
for c in "git restore ." "git restore src/mod.py" "git checkout -- ." "git checkout -f main" "git checkout main"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
# but git checkout -b (branch creation, never discards) still auto-allows
OUT=$(run_on "$(pl Bash 'git checkout -b feature/x' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "git checkout -b → allow" || bad "git checkout -b not allowed: $OUT"

# 5g) Read tools get the same secret/worktree boundary as edits (codex P1).
OUT=$(run_on "$(pl Read '' "$REPO/.env")")
[ -z "$OUT" ] && ok "Read .env → ask" || bad "Read .env auto-decided: $OUT"
OUT=$(run_on "$(pl Read '' '/etc/passwd')")
[ -z "$OUT" ] && ok "Read outside-worktree → ask" || bad "outside Read auto-decided: $OUT"
OUT=$(run_on "$(jq -nc --arg p "$REPO/src" '{"hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"path":$p}}')")
[ "$(dec "$OUT")" = "allow" ] && ok "Grep in-worktree → allow" || bad "in-worktree Grep not allowed: $OUT"
OUT=$(run_on "$(jq -nc '{"hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"path":"/etc"}}')")
[ -z "$OUT" ] && ok "Grep outside-worktree → ask" || bad "outside Grep auto-decided: $OUT"

# 5h) gh: only enumerated read/safe subcommands auto-allow; mutating ones fall to ask (codex P1).
OUT=$(run_on "$(pl Bash 'gh pr merge 268 --squash --delete-branch' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "gh pr merge → allow (intended arc)" || bad "gh pr merge not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'gh run view 5' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "gh run view → allow" || bad "gh run view not allowed: $OUT"
for c in "gh pr close 123 --delete-branch" "gh run cancel 5" "gh api repos/o/r --raw-field x=y" "gh pr edit 1 --title z"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done

# 5i) bash tools/ is restricted to test_*.sh entrypoints (codex P2).
OUT=$(run_on "$(pl Bash 'bash tools/hooks/test_lib.sh' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "bash tools test_*.sh → allow" || bad "test script not allowed: $OUT"
OUT=$(run_on "$(pl Bash 'bash tools/04-loop/run.sh' '')")
[ -z "$OUT" ] && ok "bash tools non-test script → ask" || bad "arbitrary tools script auto-decided: $OUT"

# 5j) Bash allowlist verbs must not auto-allow secret/home/outside ARGS (codex P1).
for c in "cat .env" "grep TOKEN ~/.ssh/id_rsa" "touch ~/.ssh/authorized_keys" "cat /etc/passwd" "head ../outside.txt"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
OUT=$(run_on "$(pl Bash 'cat README.md' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "cat → ask (content verbs dropped; use Read tool)" || bad "cat auto-allowed: $OUT"

# 5k) git commit --amend (history rewrite) → ask (codex P2).
OUT=$(run_on "$(pl Bash 'git commit --amend --no-edit' '')")
[ "$(dec "$OUT")" != "allow" ] && ok "git commit --amend → not auto-allowed" || bad "amend auto-allowed: $OUT"
OUT=$(run_on "$(pl Bash 'git commit -m wip' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "plain git commit → still allow" || bad "plain commit not allowed: $OUT"

# 5l) Notebook tools use notebook_path, not file_path (codex P2).
OUT=$(run_on "$(jq -nc --arg p "$REPO/nb.ipynb" '{"hook_event_name":"PreToolUse","tool_name":"NotebookEdit","tool_input":{"notebook_path":$p}}')")
[ "$(dec "$OUT")" = "allow" ] && ok "in-worktree NotebookEdit → allow" || bad "in-worktree notebook not allowed: $OUT"
OUT=$(run_on "$(jq -nc '{"hook_event_name":"PreToolUse","tool_name":"NotebookEdit","tool_input":{"notebook_path":"/etc/x.ipynb"}}')")
[ -z "$OUT" ] && ok "outside NotebookEdit → ask" || bad "outside notebook auto-decided: $OUT"

# 5m) Round-6 adversarial bypasses must NOT auto-allow (codex P1/P2).
for c in "cat '/etc/passwd'" "echo \$ANTHROPIC_API_KEY" "awk 'BEGIN{system(\"git push origin main\")}'" "git branch -d feature" "git branch --delete --force x" "printf %s \$OPENAI_API_KEY"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
# git branch (list/create) still allowed
OUT=$(run_on "$(pl Bash 'git branch' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "git branch (list) → allow" || bad "git branch list not allowed: $OUT"

# 5n) Round-7: braced/any uppercase env expansion + relative design-substrate (codex P1).
for c in "cat \${HOME}/.claude/settings.json" "mkdir \${HOME}/tmp" "cat \$TMPDIR/x"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
OUT=$(run_on "$(pl Edit '' 'design-substrate/Spec_X.md')")
[ -z "$OUT" ] && ok "relative design-substrate Edit → ask" || bad "relative design-substrate auto-decided: $OUT"

# 5o) Round-8: .git internals, admin merge, symlink escape (codex P1/P2).
for c in "cat .git/config" "touch .git/hooks/pre-commit" "chmod +x .git/hooks/pre-commit" "gh pr merge 1 --admin"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
# .github (not .git) is not mistaken for git internals (use a kept verb: git diff)
OUT=$(run_on "$(pl Bash 'git diff .github/workflows/ci.yml' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "git diff .github/... → allow (not .git)" || bad ".github path rejected as .git: $OUT"
OUT=$(run_on "$(pl Bash 'gh pr merge 1 --squash' '')")
[ "$(dec "$OUT")" = "allow" ] && ok "gh pr merge --squash → still allow" || bad "normal merge not allowed: $OUT"
# in-worktree symlink to an outside file → Read must ask (OS would follow the link out)
ln -sf /etc/passwd "$REPO/secretlink" 2>/dev/null
OUT=$(run_on "$(pl Read '' "$REPO/secretlink")")
[ -z "$OUT" ] && ok "symlink escaping worktree → ask" || bad "symlink-escape Read auto-decided: $OUT"
rm -f "$REPO/secretlink"

# 5p) Round-9: jq env dump + glob content-read → ask (content verbs dropped, codex P1).
for c in "jq -n env" "cat .*" "grep -r TOKEN config/*" "jq -n \$ENV"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
# 5q) symlink CHAIN (link → link → outside) → Read must ask (codex P2 multi-hop).
ln -sf /etc/hosts "$REPO/chain2" 2>/dev/null
ln -sf "$REPO/chain2" "$REPO/chain1" 2>/dev/null
OUT=$(run_on "$(pl Read '' "$REPO/chain1")")
[ -z "$OUT" ] && ok "symlink chain escaping worktree → ask" || bad "symlink-chain Read auto-decided: $OUT"
rm -f "$REPO/chain1" "$REPO/chain2"

# 5r) Round-10: git branch force/move → ask; Glob abs/traversal pattern → ask (codex P1/P2).
for c in "git branch -f main HEAD~1" "git branch -m old new" "git branch -C a b"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed" || bad "'$c' auto-allowed: $OUT"
done
for pat in "/etc/*" "../*.pem"; do
  OUT=$(run_on "$(jq -nc --arg p "$pat" '{"hook_event_name":"PreToolUse","tool_name":"Glob","tool_input":{"pattern":$p}}')")
  [ -z "$OUT" ] && ok "Glob pattern '$pat' → ask" || bad "Glob '$pat' auto-decided: $OUT"
done
# in-worktree Glob (relative pattern, no path) still allows
OUT=$(run_on "$(jq -nc '{"hook_event_name":"PreToolUse","tool_name":"Glob","tool_input":{"pattern":"**/*.py"}}')")
[ "$(dec "$OUT")" = "allow" ] && ok "Glob relative pattern → allow" || bad "relative Glob not allowed: $OUT"

# 5s) Round-11: path mutators/listers dropped from Bash allow (symlink-through escape); broad
#     recursive Grep gated (descendant-secret read). codex P1×2.
for c in "mkdir out/dir" "touch out/file" "chmod +x out/x" "ls out"; do
  OUT=$(run_on "$(pl Bash "$c" '')")
  [ "$(dec "$OUT")" != "allow" ] && ok "'$c' → not auto-allowed (mutator dropped)" || bad "'$c' auto-allowed: $OUT"
done
# broad Grep (no path, or repo root) → ask; specific in-worktree subpath still allows
OUT=$(run_on "$(jq -nc '{"hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"pattern":"TODO"}}')")
[ -z "$OUT" ] && ok "broad Grep (no path) → ask" || bad "broad Grep auto-decided: $OUT"
OUT=$(run_on "$(jq -nc --arg p "$REPO" '{"hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"path":$p}}')")
[ -z "$OUT" ] && ok "Grep at repo root → ask" || bad "root Grep auto-decided: $OUT"
OUT=$(run_on "$(jq -nc --arg p "$REPO/src" '{"hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"path":$p}}')")
[ "$(dec "$OUT")" = "allow" ] && ok "Grep at specific subpath → still allow" || bad "subpath Grep not allowed: $OUT"

# 6) PermissionRequest event uses the decision.behavior schema.
OUT=$(run_on "$(pl Bash 'git status' '' PermissionRequest)")
[ "$(beh "$OUT")" = "allow" ] && ok "PermissionRequest allow schema" || bad "PR allow schema wrong: $OUT"
OUT=$(run_on "$(pl Bash 'rm -rf /' '' PermissionRequest)")
[ "$(beh "$OUT")" = "deny" ] && ok "PermissionRequest deny schema" || bad "PR deny schema wrong: $OUT"

# 7) §0 worktree-live-session guard — hoisted ABOVE the inert gate, so it DENIES a
#    `git worktree remove` of a worktree with a live session in BOTH loop on/off.
WTL="$REPO/wt-live"; mkdir -p "$WTL"
FH="$REPO/home"
# Encode a worktree path EXACTLY as lib.sh's worktree_has_live_session does (printf '%s'
# strips the trailing newline so the newline is never mapped to a stray '-').
encof() { printf '%s' "$(cd "$1" && pwd -P)" | tr -c '[:alnum:]' '-'; }
SD="$FH/.claude/projects/$(encof "$WTL")"; mkdir -p "$SD"; : > "$SD/s.jsonl"   # fresh = live
runh() { printf '%s' "$1" | env HOME="$FH" CLAUDE_PROJECT_DIR="$REPO" ${2:-} bash "$HOOK"; }
OUT=$(runh "$(pl Bash "git worktree remove $WTL" '')")                       # loop OFF
[ "$(dec "$OUT")" = "deny" ] && ok "live-session worktree remove → deny (loop OFF, hoisted)" || bad "live remove not denied off-mode: $OUT"
OUT=$(runh "$(pl Bash "git worktree remove --force $WTL" '')" HARNESS_LOOP=1)  # loop ON, --force
[ "$(dec "$OUT")" = "deny" ] && ok "live-session worktree remove --force → deny (loop ON)" || bad "live --force not denied: $OUT"
OUT=$(runh "$(pl Bash "git worktree remove $WTL" '')" HARNESS_ALLOW_LIVE_WORKTREE_REMOVE=1)
[ "$(dec "$OUT")" != "deny" ] && ok "override env → not denied" || bad "override still denied: $OUT"
# stale transcript (older than window) → not a live session → not denied (inert off-mode → no output)
WTS="$REPO/wt-stale"; mkdir -p "$WTS"; SDS="$FH/.claude/projects/$(encof "$WTS")"; mkdir -p "$SDS"
: > "$SDS/old.jsonl"; touch -t 202001010000 "$SDS/old.jsonl"
OUT=$(runh "$(pl Bash "git worktree remove $WTS" '')")
[ -z "$OUT" ] && ok "stale-transcript worktree remove → not denied" || bad "stale worktree decided: $OUT"
# no transcript dir at all → not denied
WTN="$REPO/wt-none"; mkdir -p "$WTN"
OUT=$(runh "$(pl Bash "git worktree remove $WTN" '')")
[ -z "$OUT" ] && ok "no-transcript worktree remove → not denied" || bad "no-transcript decided: $OUT"

echo "----"
echo "permission_guard: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
