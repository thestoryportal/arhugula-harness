// v2 Phase-1 rubric runner (skills-first, run ONCE, cached).
//
// Executes dashboard-design/output/configurator-elevation/v2/rubric-producer.md:
// fires 4 lens-isolated, genuine skill-agents (headless `claude -p`, each invokes
// ONE design skill via the Skill tool), then deterministically synthesizes ONE
// sourcing rubric. Mirrors the built elevation-producer.mjs spawn pattern.
//
// PAID: 4 sonnet-4-6 spawns (~$0.04 each). Run via `just dashboard-rubric` so
// dotenv-load supplies ANTHROPIC_API_KEY. Each spawn is read-only (Skill + Read
// + WebFetch); no file writes by the agents, no Dribbble actions.
//
// Genuineness: each agent's stream-json is scanned for a `Skill` tool_use event;
// an agent that never invoked the Skill tool is flagged NOT-GENUINE in the report.

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const V2 = '/Users/robertrhu/Projects/arhugula-v2/dashboard-design/output/configurator-elevation/v2';
const LENS_DIR = `${V2}/_rubric-lenses`;
const MODEL = process.env.SKILLCHAIN_MODEL || 'claude-sonnet-4-6';
const TIMEOUT_MS = Number(process.env.SKILLCHAIN_TIMEOUT_MS || 420000);
const SKILLS = ['impeccable', 'design-taste-frontend', 'ui-ux-pro-max', 'frontend-design'];

const BUILD_INDEX = '/Users/robertrhu/.claude/powerline-config/static/index.html';
const BUILD_STYLE = '/Users/robertrhu/.claude/powerline-config/static/style.css';
const OWLOOPS = 'https://powerline.owloops.com/';

// FIXED constants (inherited; the skills do NOT re-derive these per the Codex redundancy finding).
const FIXED_REJECTS = [
  'standalone logos / brand-identity mockups',
  'light-mode UIs',
  'consumer/mobile app screens',
  'coding-challenge or marketing pages',
  'glassmorphism / glow / lens-flare / gradient-drenched AI-SaaS looks',
  'large rounded cards',
  'multi-color status confetti',
];
const ACCEPT_FRAME =
  'dark, warm, restrained, instrument-grade dashboard / settings / config-panel / developer-tool / console UIs; judge HIERARCHY / LAYOUT / DENSITY / TYPOGRAPHY / RESTRAINT, not palette.';

function prompt(skill) {
  return `You are a design specialist reasoning through ONE lens ONLY: the "${skill}" skill. Do not consider or imitate any other design skill.

Step 1 - ADOPT THE SKILL (genuine, verifiable): invoke \`${skill}\` via the Skill tool and fully adopt its guidance. Your run MUST show a Skill tool_use for "${skill}"; that is how genuineness is verified.

Step 2 - GROUND IN PRIMARY SOURCES (not paraphrase):
  - Read the build files: ${BUILD_INDEX} and ${BUILD_STYLE} (these define the real elements + the Almanac Noir tokens).
  - View the upstream sibling configurator via WebFetch: ${OWLOOPS} (Powerline Studio - same domain; terminal-preview + numbered sections + export). You are HEADLESS, so WebFetch substitutes for visual browsing.
  - In groundingNote, state in ONE line what these primary sources told you that a generic Dribbble search would miss.

Step 3 - EMIT, through the "${skill}" lens ONLY:
  (a) 4-6 Dribbble search queries your lens would hunt, in the project's vocabulary (configuration dashboard / settings configurator / statusline / control panel / token-matched terms like "amber dark", "warm dark monochrome", "hairline" / browser-desktop, NOT mobile);
  (b) a per-element hunt-list for brand / step-heads / terminal-preview: the specific STRUCTURAL pattern your lens looks for in each;
  (c) any lens-specific ACCEPT nuance beyond the fixed frame below.

FIXED GIVENS - do NOT re-derive these (they are inherited constants, not your job):
  REJECT: ${FIXED_REJECTS.join('; ')}.
  ACCEPT frame: ${ACCEPT_FRAME}
  ELEMENTS being elevated: brand masthead lockup (header brand in a web app, NOT a standalone logo) ; 3 numbered step-heads (number + title + one-line desc) ; terminal-preview window frame (with a column-width slider).

Your FINAL message must be STRICT JSON only - no prose, no code fences:
{"skill":"${skill}","groundingNote":"...","queries":["..."],"perElement":{"brand":["..."],"step-heads":["..."],"terminal-preview":["..."]},"acceptNuance":["..."]}`;
}

function runAgent(skill, ws) {
  return new Promise((resolve) => {
    const args = ['-p', prompt(skill), '--model', MODEL, '--output-format', 'stream-json',
      '--verbose', '--allowedTools', 'Skill,Read,WebFetch'];
    const child = spawn('claude', args, { cwd: ws, env: process.env });
    let stdout = '', stderr = '';
    const killer = setTimeout(() => child.kill('SIGKILL'), TIMEOUT_MS);
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    child.on('error', (e) => { clearTimeout(killer); resolve({ skill, error: e.message, stdout, stderr }); });
    child.on('close', (code) => {
      clearTimeout(killer);
      try { fs.writeFileSync(`${LENS_DIR}/${skill}.jsonl`, stdout + (stderr ? `\n/*STDERR*/ ${stderr}` : '')); } catch {}
      resolve({ skill, code, stdout, stderr });
    });
  });
}

function skillToolUseSeen(stdout, skill) {
  for (const line of stdout.split('\n')) {
    const t = line.trim(); if (!t) continue;
    let o; try { o = JSON.parse(t); } catch { continue; }
    const content = o?.message?.content;
    if (Array.isArray(content)) {
      for (const b of content) {
        if (b?.type === 'tool_use' && b?.name === 'Skill') {
          const input = JSON.stringify(b.input || {});
          if (input.includes(skill)) return true;
        }
      }
    }
  }
  return false;
}

function finalResultText(stdout) {
  let result = '';
  for (const line of stdout.split('\n')) {
    const t = line.trim(); if (!t) continue;
    let o; try { o = JSON.parse(t); } catch { continue; }
    if (o.type === 'result' && typeof o.result === 'string') result = o.result;
  }
  return result;
}

function extractJson(text) {
  let s = String(text).trim();
  const fence = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) s = fence[1].trim();
  else { const i = s.indexOf('{'), j = s.lastIndexOf('}'); if (i >= 0 && j > i) s = s.slice(i, j + 1); }
  return JSON.parse(s);
}

function dedupeCap(arr, cap) {
  const seen = new Set(), out = [];
  for (const x of arr || []) {
    const k = String(x).trim().toLowerCase();
    if (!k || seen.has(k)) continue;
    seen.add(k); out.push(String(x).trim());
    if (cap && out.length >= cap) break;
  }
  return out;
}

async function main() {
  fs.mkdirSync(LENS_DIR, { recursive: true });
  const ws = fs.mkdtempSync(path.join(os.tmpdir(), 'rubric-ws-'));  // clean cwd: no CLAUDE.md bleed
  process.stderr.write(`[rubric] firing ${SKILLS.length} lens-agents (model=${MODEL}) ...\n`);

  const results = await Promise.all(SKILLS.map((s) => runAgent(s, ws)));

  const lenses = [], report = [];
  for (const r of results) {
    const genuine = r.stdout ? skillToolUseSeen(r.stdout, r.skill) : false;
    let lens = null, jsonOk = false;
    if (r.stdout) {
      try { lens = extractJson(finalResultText(r.stdout)); jsonOk = !!lens && lens.skill !== undefined; } catch { jsonOk = false; }
    }
    if (jsonOk) { fs.writeFileSync(`${LENS_DIR}/${r.skill}.json`, JSON.stringify(lens, null, 2)); lenses.push(lens); }
    report.push({ skill: r.skill, exit: r.code, error: r.error || null, skillToolUseSeen: genuine, jsonValid: jsonOk });
  }

  // Synthesis (deterministic, no spawn).
  const rubric = {
    fixedRejects: FIXED_REJECTS,
    acceptFrame: ACCEPT_FRAME,
    acceptNuance: dedupeCap(lenses.flatMap((l) => l.acceptNuance || [])),
    queries: dedupeCap(lenses.flatMap((l) => l.queries || []), 8),
    hexFilters: ['#f0a830', '#15120d'],
    sort: 'Popular',
    perElement: {
      brand: dedupeCap(lenses.flatMap((l) => l.perElement?.brand || [])),
      'step-heads': dedupeCap(lenses.flatMap((l) => l.perElement?.['step-heads'] || [])),
      'terminal-preview': dedupeCap(lenses.flatMap((l) => l.perElement?.['terminal-preview'] || [])),
    },
    skillsProvenance: SKILLS,
    lensesGenuine: report.filter((r) => r.skillToolUseSeen).map((r) => r.skill),
    producedAt: new Date().toISOString(),
  };
  fs.writeFileSync(`${V2}/rubric.json`, JSON.stringify(rubric, null, 2));
  fs.writeFileSync(`${LENS_DIR}/_verification.json`, JSON.stringify({ report, ws }, null, 2));

  process.stderr.write('\n[rubric] per-lens verification:\n');
  for (const r of report) {
    process.stderr.write(`  ${r.skill.padEnd(22)} exit=${r.exit} genuine(Skill tool_use)=${r.skillToolUseSeen} json=${r.jsonValid}${r.error ? ' ERROR=' + r.error : ''}\n`);
  }
  process.stderr.write(`[rubric] wrote rubric.json  (queries=${rubric.queries.length}, genuine lenses=${rubric.lensesGenuine.length}/${SKILLS.length})\n`);
  if (rubric.lensesGenuine.length < SKILLS.length) process.exitCode = 2;  // signal: some lens not genuine / failed
}

main().catch((e) => { process.stderr.write('[rubric] FATAL ' + e.message + '\n'); process.exitCode = 1; });
