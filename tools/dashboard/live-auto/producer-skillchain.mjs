// Skill-chaining variant producer — the GENUINE version.
//
// Each loop move spawns a headless `claude` agent (read-only tools) that
// actually INVOKES the four installed .claude skills via the Skill tool, then
// returns elevation variants. This is true skill invocation in the loop (the
// Node process itself has no Skill tool; only an agent does), using the
// operator-approved Anthropic LLM behind the claude CLI.
//
// Proof: the run is captured as stream-json; the producer extracts every
// `Skill` tool_use so the orchestrator log shows which skills actually fired.
//
// Read-only by construction: allowedTools = Skill,Read,Grep,Glob (no Bash,
// no Write/Edit) so the spawned agent cannot mutate files or run impeccable's
// live-setup. Skills contribute via their SKILL.md / reference guidance.
//
// Carbonize-safe: variants reuse the element's existing global CSS classes, so
// no new CSS is lost when accept/carbonize scrubs scoped styles.
//
// Plugged via: orchestrator.mjs --producer=./producer-skillchain.mjs
// Run the orchestrator through `just` so dotenv-load gives the claude CLI its
// Anthropic credentials (never source .env directly).

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const MAIN = '/Users/robertrhu/Projects/arhugula-v2';            // repo root (for logs path)
// Clean skills-only workspace: symlinks just the 4 design skills, NO giant
// harness CLAUDE.md, so each spawn pays ~$0.035 baseline (vs ~$0.49 from repo
// root). Set up by the caller; override with SKILLCHAIN_WS.
const WS = process.env.SKILLCHAIN_WS
  || `${process.env.CLAUDE_JOB_DIR || (process.env.HOME + '/.claude/jobs')}/tmp/design-ws`;
const MODEL = process.env.SKILLCHAIN_MODEL || 'claude-sonnet-4-6';
const TIMEOUT_MS = Number(process.env.SKILLCHAIN_TIMEOUT_MS || 540000);
const LOGDIR = `${MAIN}/.claude/worktrees/r-600-pattern-bake-in-sweep/tools/dashboard/live-auto/_skillchain-logs`;

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
  return `You are a design subagent inside an autonomous dashboard-elevation loop. Your ONLY output is variant JSON. You are READ-ONLY: do NOT create, edit, or modify any file; do NOT run live mode or any setup script; do NOT use the live-* tools. Use skills purely for their design GUIDANCE.

Step 1 - invoke these four skills with the Skill tool (one at a time) and absorb their guidance:
  - impeccable        (apply the "${action}" action discipline)
  - design-taste-frontend  (apply the anti-slop "tells")
  - ui-ux-pro-max     (apply accessibility + hierarchy + status-not-by-color-alone)
  - frontend-design   (apply intentional aesthetic direction)

Step 2 - author ${count} IN-IDENTITY elevation variants of the dashboard element below. Rules:
  - REUSE the element's existing CSS classes verbatim; invent NO new class names and NO new CSS.
  - ${count} variants, each committing to a DIFFERENT primary axis (hierarchy / structure / density / copy); all clearly the SAME brand.
  - Keep all real data and numbers verbatim.
  - ZERO em-dashes and ZERO en-dashes anywhere; use hyphens.
  - Each variant is a SINGLE top-level <${tag}> element fully replacing the original.

ELEMENT TO ELEVATE:
${el.outerHTML}

Step 3 - your FINAL message must be STRICT JSON only, no prose, no code fences:
{"skillsInvoked":["impeccable","design-taste-frontend","ui-ux-pro-max","frontend-design"],"variants":[{"innerHtml":"<${tag} ...>...</${tag}>"}]}
with exactly ${count} variant entries.`;
}

function runClaude(prompt, tag) {
  const args = [
    '-p', prompt,
    '--model', MODEL,
    '--output-format', 'stream-json',
    '--verbose',
    '--allowedTools', 'Skill,Read,Grep,Glob',
  ];
  const r = spawnSync('claude', args, {
    cwd: WS,
    encoding: 'utf8',
    timeout: TIMEOUT_MS,
    maxBuffer: 64 * 1024 * 1024,
    env: process.env,
  });
  const stdout = r.stdout || '';
  // persist the raw stream for audit/proof BEFORE any throw (so timeouts are diagnosable)
  try { fs.mkdirSync(LOGDIR, { recursive: true }); fs.writeFileSync(path.join(LOGDIR, `${tag}.jsonl`), stdout + (r.stderr ? '\n/*STDERR*/ ' + r.stderr : '')); } catch {}
  if (r.error) throw new Error(`claude spawn failed: ${r.error.message} (partial stream saved to _skillchain-logs/${tag}.jsonl)`);
  if (r.status !== 0 && !stdout.trim()) throw new Error(`claude exited ${r.status}: ${(r.stderr || '').slice(0, 400)}`);
  return stdout;
}

// Parse stream-json (JSONL): collect Skill tool_uses (proof) + final result text.
function parseStream(stdout) {
  const lines = stdout.split('\n').map((l) => l.trim()).filter(Boolean);
  const skillInvocations = [];
  let resultText = '';
  for (const line of lines) {
    let obj; try { obj = JSON.parse(line); } catch { continue; }
    if (obj.type === 'assistant' && obj.message?.content) {
      for (const block of obj.message.content) {
        if (block.type === 'tool_use' && (block.name === 'Skill' || /skill/i.test(block.name))) {
          const sk = block.input?.skill || block.input?.name || JSON.stringify(block.input);
          skillInvocations.push(sk);
        }
      }
    }
    if (obj.type === 'result' && typeof obj.result === 'string') resultText = obj.result;
  }
  return { skillInvocations, resultText };
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
      const { skillInvocations, resultText } = parseStream(stdout);

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

      // PROOF the skills actually fired (Skill tool_uses from the agent's stream)
      const invoked = skillInvocations.length ? skillInvocations.join(', ') : '(none captured)';
      const claimed = Array.isArray(parsed.skillsInvoked) ? parsed.skillsInvoked.join(', ') : '?';
      process.stderr.write(
        `  [skillchain] Skill tool_uses observed: [${invoked}]\n` +
        `  [skillchain] agent self-report skillsInvoked: [${claimed}]\n` +
        `  [skillchain] taste-lint gate: ${lintNotes.length ? lintNotes.join(' ') : 'clean'}  variants:${variants.length}  model:${MODEL}\n`
      );

      return { scopedCss: '', variants };
    },
  };
}
