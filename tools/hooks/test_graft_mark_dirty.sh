#!/usr/bin/env bash
# Witness for U-SR-09 b5 (plan §8 R2): the graft post-edit hook replaced by a dirty-flag-only
# shim. Sections 1-3 are hermetic: a FAKE @nanonets/graft package under the throwaway
# project's node_modules exports the two functions the shim delegates to (`editedFilePath`,
# `patchStats`) and records what it was asked to write, plus a `main` that FAILS if called --
# so the shim is proven to (a) resolve the project-local package first, (b) route the edited
# path through graft's own resolver, (c) write ONLY {dirty, lastFile} through graft's own
# writer, and (d) never fall into the stock `post-edit` path. Section 4 is the timing
# witness against the [B] F8 baseline the unit names; section 5 runs only where the real
# graft package is installed and checks the same shim flips dirty in a real stats.json.

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SHIM="$ROOT/.claude/helpers/graft-mark-dirty.cjs"
SETTINGS="$ROOT/.claude/settings.json"
BASELINE_MEDIAN_S="8.9"   # [B] F8: the pre-fix per-edit hook median this unit is judged against

PASS=0; FAIL=0
ok()  { echo "  ok: $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
command -v node >/dev/null 2>&1 || { echo "FATAL: node not on PATH"; exit 1; }
[ -f "$SHIM" ] || { echo "FATAL: missing $SHIM"; exit 1; }

# --- 0. the registration (codex u-sr-09 r1 P3): the PostToolUse edit matcher runs THIS shim
# and no longer the stock `graft-hooks.cjs post-edit` -- reverting the settings line must red.
python3 - "$SETTINGS" <<'EOF' && ok "settings.json: a Write|Edit|MultiEdit PostToolUse group runs graft-mark-dirty.cjs and no hook runs graft-hooks.cjs post-edit" || bad "settings.json registration drifted (see python output above)"
import json, sys
d = json.load(open(sys.argv[1]))["hooks"]
cmds = [(row.get("matcher"), h["command"]) for row in d.get("PostToolUse", []) for h in row.get("hooks", [])]
shim = [m for m, c in cmds if c.endswith('/.claude/helpers/graft-mark-dirty.cjs"')]
stock = [c for _, c in cmds if "graft-hooks.cjs\" post-edit" in c]
ok = shim and all(set(str(m).split("|")) >= {"Write", "Edit", "MultiEdit"} for m in shim) and not stock
if not ok:
    print(f"shim matchers={shim} stock post-edit entries={stock}")
sys.exit(0 if ok else 1)
EOF

REPO="$(mktemp -d)"; { [ -n "$REPO" ] && [ -d "$REPO" ]; } || { echo "FATAL: mktemp -d failed"; exit 1; }
trap 'rm -rf "$REPO"' EXIT
OUT="$REPO/out.txt"
PKG="$REPO/node_modules/@nanonets/graft"; mkdir -p "$PKG/dist/claude"
printf '{"name":"@nanonets/graft","version":"0.0.0-fake","type":"module"}\n' > "$PKG/package.json"
cat > "$PKG/dist/claude/hooks.js" <<'EOF'
export function editedFilePath(input, dir) {
  const direct = input?.tool_input?.file_path;
  if (typeof direct === 'string' && direct.trim()) return direct;
  const cmd = input?.tool_input?.command;           // Codex apply_patch shape
  const m = typeof cmd === 'string' ? /^\*\*\*\s+(?:Add|Update)\s+File:\s+(.+?)\s*$/m.exec(cmd) : null;
  return m ? `${dir}/${m[1]}` : null;
}
export async function main() { throw new Error('stock post-edit path entered'); }
EOF
cat > "$PKG/dist/claude/state.js" <<'EOF'
import { mkdirSync, writeFileSync } from 'node:fs';
export function patchStats(dir, patch) {
  if (process.env.GRAFT_FAKE_THROW) throw new Error('fake patchStats failure');
  mkdirSync(`${dir}/graft/.cache`, { recursive: true });
  writeFileSync(`${dir}/graft/.cache/fake-patch.json`, JSON.stringify({ dir, patch }));
}
EOF
RECORD="$REPO/graft/.cache/fake-patch.json"

run_shim() { # <payload-json>; stdout+stderr -> $OUT; echoes rc
  rm -f "$RECORD"
  printf '%s' "$1" | CLAUDE_PROJECT_DIR="$REPO" node "$SHIM" > "$OUT" 2>&1
  echo $?
}
bytes() { wc -c < "$OUT" | tr -d ' '; }
recorded() { python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(json.dumps(d["patch"], sort_keys=True), d["dir"])' "$RECORD" 2>/dev/null; }

# --- 1. an Edit marks dirty with ONLY {dirty, lastFile}, silently ------------------------
rc=$(run_shim "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$REPO/tools/x.py\"}}")
[ "$rc" -eq 0 ] && [ "$(bytes)" -eq 0 ] && ok "Edit -> exit 0, 0 bytes" || bad "Edit -> rc=$rc, $(bytes) bytes: $(head -c 300 "$OUT")"
[ "$(recorded)" = "{\"dirty\": true, \"lastFile\": \"x.py\"} $REPO" ] && ok "patchStats called with exactly {dirty:true,lastFile} on the project dir" || bad "patchStats record: $(recorded)"
[ -f "$OUT" ] && ! grep -q "stock post-edit path" "$OUT" && ok "the stock post-edit path (graft check) is never entered" || bad "stock path entered"

# --- 2. the Codex apply_patch shape goes through graft's own resolver ----------------------
rc=$(run_shim '{"tool_name":"apply_patch","tool_input":{"command":"*** Begin Patch\n*** Update File: tools/y.py\n*** End Patch"}}')
[ "$rc" -eq 0 ] && [ "$(recorded)" = "{\"dirty\": true, \"lastFile\": \"y.py\"} $REPO" ] && ok "apply_patch shape -> lastFile y.py via editedFilePath" || bad "apply_patch: rc=$rc record=$(recorded)"

# --- 3. graft's own output dir, a payload without a path, garbage: no write, exit 0 --------
rc=$(run_shim "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$REPO/graft/INDEX.md\"}}")
[ "$rc" -eq 0 ] && [ ! -f "$RECORD" ] && ok "an edit under graft/ is not a dirtying edit" || bad "graft/ edit: rc=$rc recorded=$([ -f "$RECORD" ] && echo yes || echo no)"
rc=$(run_shim '{"tool_name":"Edit","tool_input":{}}')
[ "$rc" -eq 0 ] && [ ! -f "$RECORD" ] && [ "$(bytes)" -eq 0 ] && ok "no file_path -> nothing written, silent" || bad "no file_path: rc=$rc $(bytes) bytes"
rc=$(run_shim 'not json')
[ "$rc" -eq 0 ] && [ ! -f "$RECORD" ] && ok "garbage payload -> exit 0, nothing written" || bad "garbage payload: rc=$rc"
# codex u-sr-09 r3: a failure AFTER resolution (patchStats throwing) is not an exit 0 --
# the stderr line names it and the exit is 1, so a stale graph never hides behind a green hook
rm -f "$RECORD"
printf '%s' "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$REPO/tools/x.py\"}}" | GRAFT_FAKE_THROW=1 CLAUDE_PROJECT_DIR="$REPO" node "$SHIM" > "$OUT" 2>&1; rc=$?
[ "$rc" -eq 1 ] && grep -q 'fake patchStats failure' "$OUT" && grep -q 'NOT marked dirty' "$OUT" && ok "patchStats failure -> exit 1 with the cause on stderr" || bad "patchStats failure -> rc=$rc: $(head -c 300 "$OUT")"

# --- 4. timing against the [B] F8 baseline (the unit's stated witness) --------------------
# The hermetic path (fake package) measures the shim's own cost: node start + two dynamic
# imports + one write. Five runs, the median must sit under the 8.9 s baseline median --
# a bound with ~50x headroom so load never flakes it; the real numbers are on the commit.
P="{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$REPO/tools/x.py\"}}"
MED=$(python3 - "$SHIM" "$REPO" "$P" <<'EOF'
import statistics, subprocess, sys, time
shim, repo, payload = sys.argv[1:4]
t = []
for _ in range(5):
    s = time.monotonic()
    subprocess.run(["node", shim], input=payload.encode(), env={"CLAUDE_PROJECT_DIR": repo, "PATH": __import__("os").environ["PATH"]}, capture_output=True)
    t.append(time.monotonic() - s)
print(f"{statistics.median(t):.3f}")
EOF
)
echo "  measured: hermetic shim median ${MED}s over 5 runs (baseline median ${BASELINE_MEDIAN_S}s)"
python3 -c 'import sys; sys.exit(0 if float(sys.argv[1]) < float(sys.argv[2]) else 1)' "$MED" "$BASELINE_MEDIAN_S" \
  && ok "post-fix median ${MED}s < [B] F8 baseline ${BASELINE_MEDIAN_S}s" || bad "post-fix median ${MED}s is not under the ${BASELINE_MEDIAN_S}s baseline"

# --- 5. the real package (presence-gated, stated loudly) ------------------------------------
REAL="$(mktemp -d)"; trap 'rm -rf "$REPO" "$REAL"' EXIT
printf '%s' "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$REAL/a.py\"}}" | CLAUDE_PROJECT_DIR="$REAL" node "$SHIM" > "$OUT" 2>&1; rc=$?
if grep -q "not resolvable" "$OUT"; then
  echo "  @nanonets/graft not installed: real-package check NOT run (the shim reported it and exited $rc) -- recorded on the U-SR-09 PR"
  [ "$rc" -eq 1 ] && ok "unresolvable package -> exit 1 with a stderr notice (codex r3: never a silent green)" || bad "unresolvable package -> rc=$rc"
else
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("dirty") is True and d.get("lastFile")=="a.py" else 1)' "$REAL/graft/.cache/stats.json" 2>/dev/null \
    && ok "real graft: stats.json now carries dirty:true, lastFile a.py (rc=$rc, $(bytes) bytes)" \
    || bad "real graft: stats.json not flipped (rc=$rc): $(head -c 300 "$OUT"; cat "$REAL/graft/.cache/stats.json" 2>/dev/null)"
fi

echo "---"; echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
