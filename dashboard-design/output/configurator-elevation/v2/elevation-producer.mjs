// v2 elevation producer for the impeccable live-auto loop.
//
// Difference from v1 (producer-skillchain-dribbble.mjs, archived): this producer
// does NOT invoke the 4 skills and does NOT touch Dribbble. The skills already ran
// once (Phase 1 -> rubric.json); reference selection already happened (operator).
// This producer authors carbonize-safe markup variants for ONE element, grounded in
// TEXT context injected up front: (a) the per-element reference PATTERNS the operator
// selected, (b) the rubric's accept criteria. CSS-level elevation (K2) is authored
// SEPARATELY by the caller in style.css/app.js - NOT here (the loop stays markup-only).
//
// Env:
//   SKILLCHAIN_RUBRIC        path to v2/rubric.json (accept criteria + per-element hunt-list)
//   SKILLCHAIN_REFS_PATTERNS path to refs-patterns.json ({ "<element>": ["pattern", ...] })
//   SKILLCHAIN_WS / _MODEL / _TIMEOUT_MS / _LOGDIR / _CWD   as before (clean WS, no skills needed)
// Plugged via: orchestrator.mjs --producer=./v2/elevation-producer.mjs

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const ELEV = '/Users/robertrhu/Projects/arhugula-v2/dashboard-design/output/configurator-elevation';
const WS = process.env.SKILLCHAIN_WS || `${process.env.CLAUDE_JOB_DIR || (process.env.HOME + '/.claude/jobs')}/tmp/elevate-ws`;
const CWD = process.env.SKILLCHAIN_CWD || WS;
const MODEL = process.env.SKILLCHAIN_MODEL || 'claude-sonnet-4-6';
const TIMEOUT_MS = Number(process.env.SKILLCHAIN_TIMEOUT_MS || 300000);
const LOGDIR = process.env.SKILLCHAIN_LOGDIR || `${ELEV}/v2/_elevate-logs`;
const RUBRIC_PATH = process.env.SKILLCHAIN_RUBRIC || `${ELEV}/v2/rubric.json`;
const REFS_PATH = process.env.SKILLCHAIN_REFS_PATTERNS || `${ELEV}/v2/refs-patterns.json`;

function readJson(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } }
const RUBRIC = readJson(RUBRIC_PATH) || {};
const REFS = readJson(REFS_PATH) || {};

const EM = String.fromCharCode(8212), EN = String.fromCharCode(8211);
function tasteLint(html) {
  const fixes = []; let out = String(html);
  if (out.includes(EM)) { fixes.push('em-dash'); out = out.split(EM).join('-'); }
  if (out.includes(EN)) { fixes.push('en-dash'); out = out.split(EN).join('-'); }
  return { clean: out, fixes };
}

function elementKey(event) {
  // map the move's element hint to a refs/rubric key
  const cls = (event.classes || '') + '';
  if (/brand/.test(cls)) return 'brand';
  if (/step-head/.test(cls)) return 'step-heads';
  if (/approx|term|preview/.test(cls)) return 'terminal-preview';
  return 'overall';
}

function buildPrompt(event) {
  const el = event.element || {};
  const tag = el.tagName || 'div';
  const count = event.count || 3;
  const action = (event.action && /^[a-z]+$/.test(event.action)) ? event.action : 'impeccable';
  const key = elementKey(event);
  const patterns = (REFS[key] || REFS.overall || []);
  const accept = [RUBRIC.acceptFrame, ...(RUBRIC.acceptNuance || [])].filter(Boolean).join(' ');
  const hunt = (RUBRIC.perElement && RUBRIC.perElement[key]) || [];
  return `You are elevating ONE element of a dark "Almanac Noir" statusline-configurator UI. Output ONLY variant JSON. You are READ-ONLY: do NOT edit files, do NOT invoke any skill, do NOT browse. The design guidance is already distilled below - apply it directly.

REFERENCE PATTERNS to apply for this element (${key}), distilled from operator-selected references:
${patterns.length ? patterns.map((p) => `  - ${p}`).join('\n') : '  - (none provided; use the rubric + Almanac Noir restraint)'}

RUBRIC accept criteria: ${accept || '(dark, warm, instrument-grade, hairline, restrained)'}
Per-element hunt-list: ${hunt.length ? hunt.join('; ') : '(n/a)'}

Author ${count} IN-IDENTITY elevation variants of the element below, applying the "${action}" action and the reference patterns. Rules:
  - REUSE the element's existing CSS classes verbatim; invent NO new class names and NO new CSS (markup hierarchy only - CSS-level changes are handled separately by the caller).
  - ${count} variants, each committing to a DIFFERENT primary axis (hierarchy / structure / density / copy); all clearly the SAME brand.
  - Keep all real data/numbers verbatim. ZERO em-dashes and en-dashes; hyphens only.
  - Each variant is a SINGLE top-level <${tag}> element fully replacing the original.

ELEMENT TO ELEVATE:
${el.outerHTML}

FINAL message: STRICT JSON only, no prose/fences:
{"element":"${key}","appliedPatterns":["..."],"variants":[{"innerHtml":"<${tag} ...>...</${tag}>"}]}
with exactly ${count} variant entries.`;
}

function runClaude(prompt, tag) {
  const args = ['-p', prompt, '--model', MODEL, '--output-format', 'stream-json', '--verbose', '--allowedTools', 'Read'];
  const r = spawnSync('claude', args, { cwd: CWD, encoding: 'utf8', timeout: TIMEOUT_MS, maxBuffer: 64 * 1024 * 1024, env: process.env });
  const stdout = r.stdout || '';
  try { fs.mkdirSync(LOGDIR, { recursive: true }); fs.writeFileSync(path.join(LOGDIR, `${tag}.jsonl`), stdout + (r.stderr ? '\n/*STDERR*/ ' + r.stderr : '')); } catch {}
  if (r.error) throw new Error(`claude spawn failed: ${r.error.message}`);
  if (r.status !== 0 && !stdout.trim()) throw new Error(`claude exited ${r.status}: ${(r.stderr || '').slice(0, 400)}`);
  return stdout;
}

function parseStream(stdout) {
  let resultText = '';
  for (const line of stdout.split('\n').map((l) => l.trim()).filter(Boolean)) {
    let o; try { o = JSON.parse(line); } catch { continue; }
    if (o.type === 'result' && typeof o.result === 'string') resultText = o.result;
  }
  return resultText;
}

function extractJson(text) {
  let s = String(text).trim();
  const fence = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) s = fence[1].trim();
  else { const i = s.indexOf('{'), j = s.lastIndexOf('}'); if (i >= 0 && j > i) s = s.slice(i, j + 1); }
  return JSON.parse(s);
}

export default function createProducer() {
  return {
    async generateVariants(event) {
      const want = event.count || 3;
      const tagId = event.id || String(event.classes || 'el');
      const stdout = runClaude(buildPrompt(event), tagId);
      let parsed;
      try { parsed = extractJson(parseStream(stdout)); }
      catch (e) { throw new Error('elevation producer: unparseable variants JSON: ' + e.message); }
      let variants = Array.isArray(parsed.variants) ? parsed.variants : [];
      if (!variants.length) throw new Error('elevation producer: 0 variants');
      while (variants.length < want) variants.push({ ...variants[variants.length - 1] });
      variants = variants.slice(0, want).map((v) => ({ innerHtml: tasteLint(v.innerHtml || '').clean }));
      process.stderr.write(`  [v2-elevate] element=${elementKey(event)} patterns=${(REFS[elementKey(event)] || []).length} variants=${variants.length} model=${MODEL}\n`);
      return { scopedCss: '', variants };
    },
  };
}
