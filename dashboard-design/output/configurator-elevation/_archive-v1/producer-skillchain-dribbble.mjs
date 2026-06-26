// Dribbble-grounded skill-chaining variant producer (sandbox copy of
// tools/dashboard/live-auto/producer-skillchain.mjs).
//
// Difference from the base producer: the spawned read-only agent ALSO gets the
// read-only Dribbble MCP tools, and its prompt requires it to pull real design
// references BEFORE invoking the four skills. References inform hierarchy /
// layout / density only - colors, fonts, and CSS classes stay Almanac Noir
// (the agent reuses the element's existing classes; it invents no CSS).
//
// MCP wiring (env-configurable so I can test WS+--mcp-config vs project-cwd):
//   SKILLCHAIN_CWD          spawn cwd (default: WS). Set to a dir under the
//                           project tree if --mcp-config trust is refused.
//   SKILLCHAIN_MCP_CONFIG   path to an mcp config json; when set, passed as
//                           --mcp-config --strict-mcp-config so the spawn loads
//                           the dribbble server even outside the project tree.
//   SKILLCHAIN_LOGDIR       stream-json audit logs (default: sandbox logs dir).
//   SKILLCHAIN_WS / _MODEL / _TIMEOUT_MS  as in the base producer.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const ELEV = '/Users/robertrhu/Projects/arhugula-v2/dashboard-design/output/configurator-elevation';
const WS = process.env.SKILLCHAIN_WS
  || `${process.env.CLAUDE_JOB_DIR || (process.env.HOME + '/.claude/jobs')}/tmp/design-ws`;
const CWD = process.env.SKILLCHAIN_CWD || WS;
const MCP_CONFIG = process.env.SKILLCHAIN_MCP_CONFIG || '';
const MODEL = process.env.SKILLCHAIN_MODEL || 'claude-sonnet-4-6';
const TIMEOUT_MS = Number(process.env.SKILLCHAIN_TIMEOUT_MS || 540000);
const LOGDIR = process.env.SKILLCHAIN_LOGDIR || `${ELEV}/logs/_skillchain-logs`;

// Read-only tools: the 4 skills + read-only Dribbble (NO dribbble_auth - that is
// interactive/human-only and must already be done). No Bash/Write/Edit.
const ALLOWED_TOOLS = 'Skill,Read,Grep,Glob,mcp__dribbble__dribbble_status,mcp__dribbble__dribbble_search,mcp__dribbble__dribbble_shot';

const EM = String.fromCharCode(8212), EN = String.fromCharCode(8211);
function tasteLint(html) {
  const fixes = [];
  let out = String(html);
  if (out.includes(EM)) { fixes.push('em-dash'); out = out.split(EM).join('-'); }
  if (out.includes(EN)) { fixes.push('en-dash'); out = out.split(EN).join('-'); }
  return { clean: out, fixes };
}

function buildPrompt(event) {
  const el = event.element || {};
  const tag = el.tagName || 'div';
  const count = event.count || 3;
  const action = (event.action && /^[a-z]+$/.test(event.action)) ? event.action : 'impeccable';
  return `You are a design subagent inside an autonomous dashboard-elevation loop, elevating ONE element of a dark "Almanac Noir" statusline-configurator UI. Your ONLY output is variant JSON. You are READ-ONLY: do NOT create, edit, or modify any file; do NOT run live mode or any setup script. Use the tools below only for design GUIDANCE and references.

Step 0 - REFERENCES (mandatory). Call dribbble_status first. If it is logged in, call dribbble_search with ONE query relevant to this element and action (e.g. "dark dashboard section header", "developer tool settings panel", "terminal config UI", "instrument panel form group"), then call dribbble_shot on the 2 most relevant results to study their structure. Extract reference patterns for HIERARCHY, GROUPING, DENSITY, and LABEL TREATMENT only. Do NOT borrow their colors, fonts, or CSS - this UI keeps the Almanac Noir tokens and the element's existing classes. If dribbble_status is not logged in, note "references: unavailable" and proceed with the skills alone.

Step 1 - invoke these four skills with the Skill tool (one at a time) and absorb their guidance:
  - impeccable        (apply the "${action}" action discipline)
  - design-taste-frontend  (apply the anti-slop "tells")
  - ui-ux-pro-max     (apply accessibility + hierarchy + status-not-by-color-alone)
  - frontend-design   (apply intentional aesthetic direction)

Step 2 - author ${count} IN-IDENTITY elevation variants of the element below, grounded in the references (Step 0) + skills (Step 1). Rules:
  - REUSE the element's existing CSS classes verbatim; invent NO new class names and NO new CSS.
  - ${count} variants, each committing to a DIFFERENT primary axis (hierarchy / structure / density / copy); all clearly the SAME brand.
  - Keep all real data and numbers verbatim.
  - ZERO em-dashes and ZERO en-dashes anywhere; use hyphens.
  - Each variant is a SINGLE top-level <${tag}> element fully replacing the original.

ELEMENT TO ELEVATE:
${el.outerHTML}

Step 3 - your FINAL message must be STRICT JSON only, no prose, no code fences:
{"skillsInvoked":["impeccable","design-taste-frontend","ui-ux-pro-max","frontend-design"],"references":["<dribbble url or 'unavailable'>"],"variants":[{"innerHtml":"<${tag} ...>...</${tag}>"}]}
with exactly ${count} variant entries.`;
}

function runClaude(prompt, tag) {
  const args = [
    '-p', prompt,
    '--model', MODEL,
    '--output-format', 'stream-json',
    '--verbose',
    '--allowedTools', ALLOWED_TOOLS,
  ];
  if (MCP_CONFIG) { args.push('--mcp-config', MCP_CONFIG, '--strict-mcp-config'); }
  const r = spawnSync('claude', args, {
    cwd: CWD,
    encoding: 'utf8',
    timeout: TIMEOUT_MS,
    maxBuffer: 64 * 1024 * 1024,
    env: process.env,
  });
  const stdout = r.stdout || '';
  try { fs.mkdirSync(LOGDIR, { recursive: true }); fs.writeFileSync(path.join(LOGDIR, `${tag}.jsonl`), stdout + (r.stderr ? '\n/*STDERR*/ ' + r.stderr : '')); } catch {}
  if (r.error) throw new Error(`claude spawn failed: ${r.error.message} (partial stream saved to ${LOGDIR}/${tag}.jsonl)`);
  if (r.status !== 0 && !stdout.trim()) throw new Error(`claude exited ${r.status}: ${(r.stderr || '').slice(0, 400)}`);
  return stdout;
}

function parseStream(stdout) {
  const lines = stdout.split('\n').map((l) => l.trim()).filter(Boolean);
  const skillInvocations = [];
  const dribbbleCalls = [];
  let resultText = '';
  for (const line of lines) {
    let obj; try { obj = JSON.parse(line); } catch { continue; }
    if (obj.type === 'assistant' && obj.message?.content) {
      for (const block of obj.message.content) {
        if (block.type === 'tool_use' && (block.name === 'Skill' || /skill/i.test(block.name))) {
          const sk = block.input?.skill || block.input?.name || JSON.stringify(block.input);
          skillInvocations.push(sk);
        }
        if (block.type === 'tool_use' && /dribbble/i.test(block.name || '')) {
          dribbbleCalls.push(block.name);
        }
      }
    }
    if (obj.type === 'result' && typeof obj.result === 'string') resultText = obj.result;
  }
  return { skillInvocations, dribbbleCalls, resultText };
}

function extractVariantsJson(text) {
  let s = String(text).trim();
  const fence = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) s = fence[1].trim();
  else { const i = s.indexOf('{'), j = s.lastIndexOf('}'); if (i >= 0 && j > i) s = s.slice(i, j + 1); }
  return JSON.parse(s);
}

export default function createProducer() {
  return {
    async generateVariants(event, context = {}) {
      const want = event.count || 3;
      const tagId = event.id || String(Date.now());
      const prompt = buildPrompt(event);

      const stdout = runClaude(prompt, tagId);
      const { skillInvocations, dribbbleCalls, resultText } = parseStream(stdout);

      let parsed;
      try { parsed = extractVariantsJson(resultText); }
      catch (e) { throw new Error('skillchain: agent did not return parseable variants JSON: ' + e.message + ' :: ' + resultText.slice(0, 200)); }

      let variants = Array.isArray(parsed.variants) ? parsed.variants : [];
      if (variants.length === 0) throw new Error('skillchain: agent returned 0 variants');
      while (variants.length < want) variants.push({ ...variants[variants.length - 1] });
      variants = variants.slice(0, want);

      const lintNotes = [];
      variants = variants.map((v, i) => {
        const { clean, fixes } = tasteLint(v.innerHtml || '');
        if (fixes.length) lintNotes.push(`v${i + 1}:[${fixes.join(',')}]`);
        return { innerHtml: clean };
      });

      const invoked = skillInvocations.length ? skillInvocations.join(', ') : '(none captured)';
      const drib = dribbbleCalls.length ? dribbbleCalls.join(', ') : '(none)';
      const refs = Array.isArray(parsed.references) ? parsed.references.join(', ') : '?';
      process.stderr.write(
        `  [skillchain] Skill tool_uses observed: [${invoked}]\n` +
        `  [skillchain] Dribbble tool_uses observed: [${drib}]\n` +
        `  [skillchain] references reported: [${refs}]\n` +
        `  [skillchain] taste-lint gate: ${lintNotes.length ? lintNotes.join(' ') : 'clean'}  variants:${variants.length}  model:${MODEL}\n`
      );

      return { scopedCss: '', variants };
    },
  };
}
