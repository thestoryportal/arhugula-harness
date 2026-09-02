#!/usr/bin/env node
// PostToolUse(Write|Edit|MultiEdit): mark the graft graph dirty -- and nothing else.
// (U-SR-09 b5, plan §8 R2; [B] F8: 945 s inside 100 edit round-trips, 8.9 s median.)
//
// What the stock hook (`graft-hooks.cjs post-edit`, @nanonets/graft 0.10.1, unchanged at
// 0.16.0) does on every edit: `graft check . --json` under an 8 s child budget, then
// `patchStats({dirty, staleCount, lastFile})`, then a blast-radius emission. Measured at
// U-SR-09 on this repo (22,694 nodes): `graft check` takes 45.7-45.9 s, so the child times
// out on EVERY edit, `staleCount` is always 0 (the null result), the blast radius is 0 bytes,
// and the hook costs a flat 8.8 s per edit -- the whole [B] F8 median -- for one effect:
// `dirty: true`, which the Stop hook reads to spawn the 5.6 s `graft build`. [B]'s own arm
// ("put ruff on PATH") is falsified by the same measurement: `postedit-lint.sh` costs 0.3 s
// warm and `uv run ruff` 0.16 s vs 0.08 s direct. This shim keeps the one effect that
// happens and drops the 8 s that buys nothing.
//
// It writes through graft's OWN exported API (`patchStats` from dist/claude/state.js,
// `editedFilePath` from dist/claude/hooks.js -- the Claude-Code and Codex apply_patch edit
// shapes) so graft/.cache/stats.json keeps its one owner. [LAW:one-source-of-truth]
// Resolution order: the project's node_modules, the running node's global lib, then
// `npm root -g` (the generated shim bakes an absolute mise path; this one does not).
//
// The settings.json `timeout: 5` on this hook derives from the measured cost -- 0.147 s
// median over 5 runs with the real package on this repo (U-SR-09) -- with ~30x headroom
// for a loaded machine; the stock entry carried 10 s because its child alone needed 8.
//
// Known re-entry: `graft init` re-merges its own `post-edit` entry into .claude/settings.json
// (mergeGraftSettings); after any re-init, drop that entry again or both hooks fire.
// Exit plan: delete this shim once an upstream graft post-edit no longer runs `graft check`
// inside the hook (or derives a budget the check fits in) -- check `handlePostEdit` in the
// installed dist/claude/hooks.js.
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
const { execFileSync } = require('child_process');

const dir = process.env.CLAUDE_PROJECT_DIR || process.cwd();

function distFrom(base) {
  try {
    const pkg = require.resolve('@nanonets/graft/package.json', { paths: [base] });
    return path.join(path.dirname(pkg), 'dist', 'claude');
  } catch { return null; }
}
function globalRoot() {
  try {
    return execFileSync('npm', ['root', '-g'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim() || null;
  } catch { return null; }
}
function dist() {
  const local = distFrom(dir);
  if (local) return local;
  const nodeLib = distFrom(path.join(path.dirname(process.execPath), '..', 'lib'));
  if (nodeLib) return nodeLib;
  const gr = globalRoot();
  return gr ? distFrom(gr) : null;
}

let input = {};
try { input = JSON.parse(fs.readFileSync(0, 'utf8')); } catch { /* no/invalid payload: nothing to mark */ }

const d = dist();
if (!d) {
  console.error('[graft-mark-dirty] @nanonets/graft not resolvable -- graph NOT marked dirty');
  process.exit(0);
}
Promise.all([
  import(pathToFileURL(path.join(d, 'hooks.js')).href),
  import(pathToFileURL(path.join(d, 'state.js')).href),
]).then(([hooks, state]) => {
  const file = hooks.editedFilePath(input, dir);
  if (!file) return;
  const rel = path.relative(dir, file);
  if (rel === 'graft' || rel.startsWith('graft' + path.sep)) return; // graft's own output
  state.patchStats(dir, { dirty: true, lastFile: path.basename(file) });
}).catch((e) => {
  console.error(`[graft-mark-dirty] ${e && e.message ? e.message : e} -- graph NOT marked dirty`);
});
