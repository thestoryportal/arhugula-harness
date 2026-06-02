#!/usr/bin/env node
/**
 * orchestrator.mjs — Autonomous driver for the `impeccable` skill's live mode.
 *
 * In normal use, a HUMAN selects an element in a browser and clicks Go; the
 * browser POSTs a `generate` event to the live helper server; an AGENT
 * long-polls `/poll`, wraps the element, writes 3 variant blocks, replies
 * `done`; the human picks one and clicks accept; the browser POSTs `accept`;
 * the agent runs `live-accept.mjs` + carbonize cleanup.
 *
 * This orchestrator plays BOTH roles autonomously, with NO browser and NO LLM:
 *
 *   - The AGENT half is the canonical `runAgentLoop()` from the skill's e2e
 *     test blueprint (tests/live-e2e/agent.mjs). It owns wrap → generate
 *     variants (via a pluggable `agent.generateVariants` hook) → splice →
 *     reply `done`, and accept → live-accept → carbonize cleanup → reply.
 *     We run it concurrently in this same process under an AbortController.
 *
 *   - The HUMAN half is this file's move loop. For each move in the plan it
 *     POSTs a `generate` event to `/events`, waits (level-triggered file poll)
 *     until the agent has written variants into the target file, POSTs an
 *     `accept` event, waits until carbonize cleanup has scrubbed the file,
 *     then advances to the next move.
 *
 * The variant producer is INJECTABLE: pass your own `agent` implementing the
 * `LiveAgent` interface (see agent-blueprint.mjs — `generateVariants(event,
 * ctx)`). For autonomous smoke runs we default to a tag-aware CANNED producer
 * (createCannedProducer) that emits 3 trivial, distinct, same-tag variants and
 * NEVER calls an LLM. A real run plugs in human-authored variants by passing
 * `--producer ./my-producer.mjs` (default export = a LiveAgent) or by calling
 * runOrchestrator({ agent }) programmatically.
 *
 * Hard constraints honored: no LLM calls, no network beyond localhost, writes
 * confined to the target file + .impeccable/ journal + the live helper server.
 */

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import { randomBytes } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { runAgentLoop } from './agent-blueprint.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// Skill-scripts resolution
// ---------------------------------------------------------------------------

/**
 * Resolve the impeccable scripts dir. The live-* CLIs are cwd-sensitive
 * (git check-ignore, .impeccable/live/config.json resolution), so we always
 * run them with cwd = projectRoot. The scripts themselves live under the
 * skill install, which may be at the MAIN repo root even when projectRoot is a
 * git worktree. Resolution order: explicit override / env → projectRoot skill
 * → git common-dir parent skill (worktree → main root) → repo-relative default.
 */
export function resolveScriptsDir(projectRoot, override) {
  const candidates = [];
  if (override) candidates.push(override);
  candidates.push(path.join(projectRoot, '.claude', 'skills', 'impeccable', 'scripts'));

  // If projectRoot is a git worktree, the skill usually lives at the main
  // working tree. Resolve it from `git rev-parse --git-common-dir`.
  try {
    const commonDir = execFileSync('git', ['rev-parse', '--git-common-dir'], {
      cwd: projectRoot, encoding: 'utf-8',
    }).trim();
    const mainRoot = path.dirname(path.resolve(projectRoot, commonDir));
    candidates.push(path.join(mainRoot, '.claude', 'skills', 'impeccable', 'scripts'));
  } catch { /* not a git repo, or no worktree */ }

  for (const c of candidates) {
    if (c && fs.existsSync(path.join(c, 'live-server.mjs'))) return c;
  }
  throw new Error(
    'Could not find impeccable scripts dir. Looked in:\n  ' +
      candidates.filter(Boolean).join('\n  ') +
      '\nPass --scripts-dir=PATH or set IMPECCABLE_SCRIPTS_DIR.',
  );
}

// ---------------------------------------------------------------------------
// Canned, tag-aware variant producer (the LLM-replacement seam)
// ---------------------------------------------------------------------------

/**
 * Build a deterministic, tag-aware canned producer. Unlike the e2e fixture's
 * createFakeAgent (hardcoded to <h1 class="hero-title">), this reads the
 * picked element's tag + text from the event so a multi-move plan over
 * different elements stays faithful (variant tag matches original tag — a
 * live.md requirement: "one top-level element ... the same tag as the
 * original").
 *
 * Produces 3 visibly-distinct variants varying a different primary axis each
 * (color / weight / case), with one param knob per variant covering all three
 * param kinds (range / steps / toggle) across the set — matching the schema
 * the skill documents and the fixture exercises. NEVER calls an LLM.
 *
 * @returns {import('./agent-blueprint.mjs').LiveAgent}
 */
export function createCannedProducer() {
  return {
    async generateVariants(event, context = {}) {
      const tag = (event.element?.tagName || 'div').toLowerCase();
      const cls = firstClass(event.element) || 'live-auto-target';
      const text = textOf(event) || 'Live Auto';
      const useAstro = context.wrapInfo?.styleMode === 'astro-global-prefixed';

      const variants = [
        {
          innerHtml: `<${tag} class="${cls}">${escapeHtml(text)}</${tag}>`,
          params: [
            { id: 'lightness', kind: 'range', min: 0.3, max: 0.7, step: 0.05, default: 0.5, label: 'Lightness' },
          ],
        },
        {
          innerHtml: `<${tag} class="${cls}">${escapeHtml(text)}</${tag}>`,
          params: [
            {
              id: 'face', kind: 'steps', default: 'sans', label: 'Face',
              options: [
                { value: 'sans', label: 'Sans' },
                { value: 'serif', label: 'Serif' },
                { value: 'mono', label: 'Mono' },
              ],
            },
          ],
        },
        {
          innerHtml: `<${tag} class="${cls}">${escapeHtml(text)}</${tag}>`,
          params: [
            { id: 'italic', kind: 'toggle', default: false, label: 'Italic' },
          ],
        },
      ];

      const scopedCss = useAstro
        ? [
            `[data-impeccable-variant="1"] > ${tag} { color: oklch(var(--p-lightness, 0.5) 0.25 25); }`,
            `[data-impeccable-variant="2"] > ${tag} { font-weight: 900; }`,
            `[data-impeccable-variant="2"][data-p-face="serif"] > ${tag} { font-family: ui-serif, serif; }`,
            `[data-impeccable-variant="2"][data-p-face="mono"]  > ${tag} { font-family: ui-monospace, monospace; }`,
            `[data-impeccable-variant="3"] > ${tag} { text-transform: uppercase; letter-spacing: 0.04em; }`,
            `[data-impeccable-variant="3"][data-p-italic] > ${tag} { font-style: italic; }`,
          ].join('\n')
        : [
            '@scope ([data-impeccable-variant="1"]) {',
            `  :scope > ${tag} { color: oklch(var(--p-lightness, 0.5) 0.25 25); }`,
            '}',
            '@scope ([data-impeccable-variant="2"]) {',
            `  :scope > ${tag} { font-weight: 900; }`,
            `  :scope[data-p-face="serif"] > ${tag} { font-family: ui-serif, serif; }`,
            `  :scope[data-p-face="mono"]  > ${tag} { font-family: ui-monospace, monospace; }`,
            '}',
            '@scope ([data-impeccable-variant="3"]) {',
            `  :scope > ${tag} { text-transform: uppercase; letter-spacing: 0.04em; }`,
            `  :scope[data-p-italic] > ${tag} { font-style: italic; }`,
            '}',
          ].join('\n');

      return { scopedCss, variants };
    },
  };
}

function firstClass(element) {
  if (!element) return null;
  if (Array.isArray(element.classes) && element.classes.length) return element.classes[0];
  if (typeof element.className === 'string' && element.className.trim()) {
    return element.className.trim().split(/\s+/)[0];
  }
  return null;
}

function textOf(event) {
  const t = event.element?.textContent;
  if (typeof t === 'string' && t.trim()) return t.trim().slice(0, 80);
  const m = String(event.element?.outerHTML || '').match(/>([^<]+)</);
  return m ? m[1].trim() : null;
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ---------------------------------------------------------------------------
// Live helper server lifecycle (mirrors tests/live-e2e/session.mjs)
// ---------------------------------------------------------------------------

const VISUAL_ACTIONS = new Set([
  'impeccable', 'bolder', 'quieter', 'distill', 'polish', 'typeset',
  'colorize', 'layout', 'adapt', 'animate', 'delight', 'overdrive',
]);

function writeLiveConfig(projectRoot, targetFiles) {
  const dir = path.join(projectRoot, '.impeccable', 'live');
  fs.mkdirSync(dir, { recursive: true });
  const cfgPath = path.join(dir, 'config.json');
  const config = {
    files: targetFiles,
    insertBefore: '</body>',
    commentSyntax: 'html',
    cspChecked: true,
  };
  fs.writeFileSync(cfgPath, JSON.stringify(config, null, 2));
  return cfgPath;
}

function startLiveServer(projectRoot, scriptsDir) {
  const out = execFileSync(
    process.execPath,
    [path.join(scriptsDir, 'live-server.mjs'), '--background'],
    { cwd: projectRoot, encoding: 'utf-8' },
  );
  const line = out.trim().split('\n').filter(Boolean).pop();
  const info = JSON.parse(line);
  if (!info.port || !info.token) {
    throw new Error('live-server --background returned unexpected payload: ' + line);
  }
  return info;
}

function runInject(projectRoot, scriptsDir, port) {
  const out = execFileSync(
    process.execPath,
    [path.join(scriptsDir, 'live-inject.mjs'), '--port', String(port)],
    { cwd: projectRoot, encoding: 'utf-8', env: { ...process.env } },
  );
  const line = out.trim().split('\n').filter(Boolean).pop();
  return JSON.parse(line);
}

function stopLiveServer(projectRoot, scriptsDir, { keepInject = false } = {}) {
  const args = [path.join(scriptsDir, 'live-server.mjs'), 'stop'];
  if (keepInject) args.push('--keep-inject');
  try {
    execFileSync(process.execPath, args, { cwd: projectRoot, stdio: 'ignore' });
  } catch { /* already gone */ }
}

// ---------------------------------------------------------------------------
// The HUMAN half — POST events to /events and wait on file-state markers
// ---------------------------------------------------------------------------

function newEventId() {
  // /^[0-9a-f]{8}$/
  return randomBytes(4).toString('hex');
}

async function postEvent(base, token, event) {
  const res = await fetch(`${base}/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...event, token }),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || json.error) {
    throw new Error(`POST /events (${event.type}) rejected: ${res.status} ${JSON.stringify(json)}`);
  }
  return json;
}

/**
 * Build a `generate` event matching live-event-validation.mjs validateEvent:
 * needs {type, id(8hex), count(1-8), action∈VISUAL_ACTIONS, element.outerHTML, pageUrl}.
 */
function buildGenerateEvent({ id, move, target }) {
  const action = move.action && VISUAL_ACTIONS.has(move.action) ? move.action : 'impeccable';
  const count = Number.isInteger(move.count) && move.count >= 1 && move.count <= 8 ? move.count : 3;
  const tag = target.tag || 'div';
  const text = target.text || '';
  const spaceClasses = target.classes
    ? target.classes.split(',').map((c) => c.trim()).filter(Boolean)
    : [];
  const idAttr = target.elementId ? ` id="${target.elementId}"` : '';
  // CSS class attributes are SPACE-separated (the comma form is only the
  // live-wrap --classes flag syntax). A stub with commas would teach the
  // producer the wrong markup.
  const classAttr = spaceClasses.length ? ` class="${spaceClasses.join(' ')}"` : '';
  // Prefer the move's REAL outerHTML (the full element with its children) when
  // provided; a real browser sends the live DOM, not a skeletal stub.
  const outerHTML = move.outerHTML || `<${tag}${idAttr}${classAttr}>${escapeHtml(text)}</${tag}>`;
  return {
    type: 'generate',
    id,
    action,
    count,
    pageUrl: move.pageUrl || '/',
    freeformPrompt: move.freeformPrompt || undefined,
    element: {
      id: target.elementId || undefined,
      classes: spaceClasses,
      tagName: tag,
      textContent: text,
      outerHTML,
    },
  };
}

async function waitForFile(absFile, predicate, { label, timeoutMs = Number(process.env.ORCH_WAIT_MS || 300000), intervalMs = 50 }) {
  const deadline = Date.now() + timeoutMs;
  let last = '';
  while (Date.now() < deadline) {
    try {
      last = await fsp.readFile(absFile, 'utf-8');
      if (predicate(last)) return last;
    } catch { /* file briefly mid-write */ }
    await delay(intervalMs);
  }
  throw new Error(
    `Timed out waiting for: ${label} (${timeoutMs}ms) on ${path.basename(absFile)}`,
  );
}

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------------------------------------------------------------------------
// Move resolution — translate plan selector hints to a wrap target
// ---------------------------------------------------------------------------

/**
 * Resolve a plan move's selector hints against the on-disk target file so we
 * pick the right element's tag/text even when hints are partial. Returns the
 * wrap target object live-wrap consumes (elementId / classes / tag / text).
 */
function resolveMoveTarget(move, fileSource) {
  const hints = move;
  let tag = hints.tag || null;
  let elementId = hints.elementId || hints.id || null;
  const classes = Array.isArray(hints.classes)
    ? hints.classes.join(',')
    : (hints.classes || null);
  let text = hints.text || null;

  // If an id is given, recover tag + text from source for fidelity.
  if (elementId) {
    const re = new RegExp(`<([a-zA-Z][\\w-]*)\\b[^>]*\\bid=["']${escapeRegExp(elementId)}["'][^>]*>([\\s\\S]*?)<\\/\\1>`);
    const m = fileSource.match(re);
    if (m) {
      tag = tag || m[1];
      if (!text) text = stripTags(m[2]).trim().slice(0, 80) || null;
    }
  } else if (classes) {
    const firstCls = classes.split(',')[0].trim();
    const re = new RegExp(`<([a-zA-Z][\\w-]*)\\b[^>]*\\bclass=["'][^"']*\\b${escapeRegExp(firstCls)}\\b[^"']*["'][^>]*>([\\s\\S]*?)<\\/\\1>`);
    const m = fileSource.match(re);
    if (m) {
      tag = tag || m[1];
      if (!text) text = stripTags(m[2]).trim().slice(0, 80) || null;
    }
  }

  return {
    elementId: elementId || undefined,
    classes: classes || undefined,
    tag: tag || 'div',
    text: text || undefined,
  };
}

function stripTags(s) { return String(s).replace(/<[^>]*>/g, ' '); }
function escapeRegExp(v) { return String(v).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

// ---------------------------------------------------------------------------
// Orchestration
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} Move
 * @property {string=} elementId
 * @property {string|string[]=} classes
 * @property {string=} tag
 * @property {string=} text          Disambiguating text snippet for live-wrap.
 * @property {string=} action        One of the 12 visual actions; default 'impeccable'.
 * @property {string=} freeformPrompt
 * @property {number=} count         1-8; default 3.
 * @property {number|string=} acceptVariant  Which variant to persist; default 1.
 * @property {string=} pageUrl       Default '/'.
 */

/**
 * Run the full autonomous loop.
 *
 * @param {Object} opts
 * @param {string} opts.targetFile          Path to target HTML (relative to projectRoot or absolute).
 * @param {Move[]} opts.plan                Declarative array of moves.
 * @param {import('./agent-blueprint.mjs').LiveAgent} [opts.agent]  Variant producer (default: canned).
 * @param {string} [opts.projectRoot]       cwd for the cwd-sensitive live-* CLIs (default process.cwd()).
 * @param {string} [opts.scriptsDir]        Override impeccable scripts dir.
 * @param {boolean} [opts.inject=true]      Inject live.js into the file (harmless for the file-write path).
 * @param {(msg: string) => void} [opts.log]
 * @returns {Promise<{ok: boolean, moves: number, file: string, clean: boolean}>}
 */
export async function runOrchestrator({
  targetFile,
  plan,
  agent = createCannedProducer(),
  projectRoot = process.cwd(),
  scriptsDir,
  inject = true,
  log = (m) => console.log(m),
}) {
  if (!Array.isArray(plan) || plan.length === 0) throw new Error('plan must be a non-empty array of moves');
  const resolvedScripts = resolveScriptsDir(projectRoot, scriptsDir || process.env.IMPECCABLE_SCRIPTS_DIR);
  const absFile = path.isAbsolute(targetFile) ? targetFile : path.resolve(projectRoot, targetFile);
  const relFile = path.relative(projectRoot, absFile);
  if (!fs.existsSync(absFile)) throw new Error(`target file does not exist: ${absFile}`);

  log(`[orchestrator] project root: ${projectRoot}`);
  log(`[orchestrator] scripts dir:  ${resolvedScripts}`);
  log(`[orchestrator] target file:  ${relFile}`);

  // a. config + boot live-server
  writeLiveConfig(projectRoot, [relFile]);
  const live = startLiveServer(projectRoot, resolvedScripts);
  const base = `http://127.0.0.1:${live.port}`;
  log(`[orchestrator] live-server up on port ${live.port}`);

  // b. ensure live.js injected (not strictly required for the file-write path)
  let injected = false;
  if (inject) {
    const r = runInject(projectRoot, resolvedScripts, live.port);
    injected = r.ok === true;
    log(`[orchestrator] live-inject: ${injected ? `injected into ${r.file || relFile}` : JSON.stringify(r)}`);
  } else {
    log('[orchestrator] live-inject skipped (--no-inject); file-write path does not require it');
  }

  // Agent half — the canonical poll/wrap/write/accept loop. wrapTarget is a
  // FUNCTION so each move wraps the element the picker event named.
  const abort = new AbortController();
  const wrapTarget = (event) => ({
    elementId: event.element?.id || undefined,
    classes: Array.isArray(event.element?.classes) && event.element.classes.length
      ? event.element.classes.join(',')
      : undefined,
    tag: event.element?.tagName || 'div',
    text: (event.element?.textContent || '').trim() || undefined,
    // Pin wrap to THIS target file so it can't roam to a sibling file that
    // shares the same element (e.g. another rendered dashboard snapshot).
    file: relFile,
  });

  const agentDone = runAgentLoop({
    tmp: projectRoot,
    scriptsDir: resolvedScripts,
    port: live.port,
    token: live.token,
    agent,
    wrapTarget,
    signal: abort.signal,
    log: (m) => log('  [agent] ' + m),
  });

  let movesDone = 0;
  try {
    for (let i = 0; i < plan.length; i++) {
      const move = plan[i];
      const source = await fsp.readFile(absFile, 'utf-8');
      const target = resolveMoveTarget(move, source);
      const id = newEventId();
      const acceptVariant = String(move.acceptVariant ?? 1);

      log(`\n[move ${i + 1}/${plan.length}] id=${id} action=${move.action || 'impeccable'} ` +
          `target=<${target.tag}${target.elementId ? '#' + target.elementId : ''}` +
          `${target.classes ? '.' + target.classes.split(',')[0] : ''}> accept=v${acceptVariant}`);

      // 1. POST generate (the human's "Go")
      await postEvent(base, live.token, buildGenerateEvent({ id, move, target }));
      log('  [human] POST /events {type:generate} ->200; waiting for variants...');

      // 2. Wait until the agent wrote variants into the file (level-triggered).
      await waitForFile(absFile, (s) => s.includes('data-impeccable-variant="1"'), {
        label: 'agent wrote variant block',
      });
      log('  [human] variants present in file');

      // 3. POST accept (the human's pick)
      await postEvent(base, live.token, { type: 'accept', id, variantId: acceptVariant });
      log(`  [human] POST /events {type:accept,variantId:${acceptVariant}} ->200; waiting for cleanup...`);

      // 4. Wait until carbonize cleanup has scrubbed the file. The agent's
      //    accept handler runs live-accept.mjs then runCarbonizeCleanup, which
      //    removes the variant wrapper + carbonize markers. Done = no variant
      //    wrappers and no carbonize markers remain.
      await waitForFile(absFile, (s) =>
        !s.includes('data-impeccable-variant=') &&
        !s.includes('impeccable-carbonize-start') &&
        !s.includes('impeccable-variants-start'),
        { label: 'carbonize cleanup complete' });
      log('  [human] accept persisted + file scrubbed clean');
      movesDone++;
    }
  } finally {
    // Stop the agent loop, then the server (server stop runs live-inject --remove).
    abort.abort();
    await agentDone.catch(() => {});
    stopLiveServer(projectRoot, resolvedScripts, { keepInject: false });
    log('\n[orchestrator] agent loop aborted; live-server stopped + live.js removed');
  }

  // Final clean-state verification.
  const final = await fsp.readFile(absFile, 'utf-8');
  const leftovers = [
    'impeccable-variants-start',
    'impeccable-carbonize-start',
    'data-impeccable-variant',
    `:${live.port}/live.js`,
    'live.js"></script>',
  ].filter((marker) => final.includes(marker));
  const clean = leftovers.length === 0;
  if (!clean) log(`[orchestrator] WARNING leftover markers: ${leftovers.join(', ')}`);
  log(`[orchestrator] DONE moves=${movesDone}/${plan.length} clean=${clean}`);

  return { ok: movesDone === plan.length && clean, moves: movesDone, file: relFile, clean };
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const out = { _: [] };
  for (const a of argv) {
    const m = a.match(/^--([^=]+)(?:=(.*))?$/);
    if (m) out[m[1]] = m[2] === undefined ? true : m[2];
    else out._.push(a);
  }
  return out;
}

async function loadPlan(planPath, projectRoot) {
  const abs = path.isAbsolute(planPath) ? planPath : path.resolve(projectRoot, planPath);
  const mod = await import(pathToFileURL(abs).href);
  const plan = mod.default ?? mod.plan ?? mod.moves;
  if (!Array.isArray(plan)) throw new Error(`plan module ${planPath} must default-export an array of moves`);
  return plan;
}

async function loadProducer(producerPath, projectRoot) {
  const abs = path.isAbsolute(producerPath) ? producerPath : path.resolve(projectRoot, producerPath);
  const mod = await import(pathToFileURL(abs).href);
  const factory = mod.default ?? mod.createProducer ?? mod.createAgent;
  const agent = typeof factory === 'function' ? factory() : factory;
  if (!agent || typeof agent.generateVariants !== 'function') {
    throw new Error(`producer module ${producerPath} must export a LiveAgent (default fn/object with generateVariants)`);
  }
  return agent;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.h) {
    console.log(`Usage: node tools/dashboard/live-auto/orchestrator.mjs --file=PATH --plan=PATH [options]

Drives the impeccable live-mode loop autonomously (no browser, no LLM).

Required:
  --file=PATH        Target HTML file (relative to --root or absolute).
  --plan=PATH        JS/JSON module default-exporting an array of moves.

Options:
  --root=PATH        Project root / cwd for cwd-sensitive live-* CLIs (default: cwd).
  --producer=PATH    Module default-exporting a LiveAgent (variant producer).
                     Default: built-in tag-aware canned producer (no LLM).
  --scripts-dir=PATH Override impeccable scripts dir.
  --no-inject        Skip live.js injection (file-write path does not need it).
  --help             Show this help.

A move = { elementId?, classes?, tag?, text?, action?, freeformPrompt?, count?, acceptVariant?, pageUrl? }`);
    return;
  }
  if (!args.file || !args.plan) {
    console.error('error: --file and --plan are required. Run with --help.');
    process.exit(2);
  }
  const projectRoot = args.root ? path.resolve(args.root) : process.cwd();
  const plan = await loadPlan(args.plan, projectRoot);
  const agent = args.producer ? await loadProducer(args.producer, projectRoot) : createCannedProducer();

  const result = await runOrchestrator({
    targetFile: args.file,
    plan,
    agent,
    projectRoot,
    scriptsDir: args['scripts-dir'],
    inject: !args['no-inject'],
  });
  process.exit(result.ok ? 0 : 1);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((err) => {
    console.error('[orchestrator] FATAL:', err.stack || err.message);
    process.exit(1);
  });
}
