export const meta = {
  name: 'dribbble-converge',
  description: 'Unanimous 4-skill convergence on which Dribbble references suit the Almanac Noir configurator',
  phases: [
    { title: 'Evaluate', detail: '4 skill-adopting agents independently score each candidate (image-grounded)' },
    { title: 'Converge', detail: 'keep only references all four skills endorse (unanimous)' },
  ],
}

// args = { pool: [{id, title, url, image, localImagePath, element}], ui: "<desc>" }
const SKILLS = ['impeccable', 'design-taste-frontend', 'ui-ux-pro-max', 'frontend-design'];
const IMG = '/Users/robertrhu/Projects/arhugula-v2/dashboard-design/output/configurator-elevation/refs-images';
const pool = [
  { id: 1, title: 'SYNTAX - Clean, Code-Inspired SaaS Logo', url: 'https://dribbble.com/shots/27277370', element: 'brand', localImagePath: `${IMG}/id1.png` },
  { id: 2, title: 'Ovonex Team Logo - Lettermark O for SaaS/AI/Cloud', url: 'https://dribbble.com/shots/26233856', element: 'brand', localImagePath: `${IMG}/id2.jpg` },
  { id: 3, title: 'EXPERI/MENTAL - Finance brand', url: 'https://dribbble.com/shots/27418916', element: 'brand', localImagePath: `${IMG}/id3.png` },
  { id: 4, title: 'Coding Interface', url: 'https://dribbble.com/shots/2652428', element: 'terminal-preview', localImagePath: `${IMG}/id4.png` },
  { id: 5, title: 'Brackets concept', url: 'https://dribbble.com/shots/3691838', element: 'terminal-preview', localImagePath: `${IMG}/id5.png` },
  { id: 6, title: 'Dark Mode Bento Grid UI with Analytics', url: 'https://dribbble.com/shots/27456998', element: 'overall', localImagePath: `${IMG}/id6.png` },
  { id: 7, title: 'Alps - Premium Dark Admin Template', url: 'https://dribbble.com/shots/24071167', element: 'overall', localImagePath: `${IMG}/id7.png` },
  { id: 8, title: 'Alps - Support Template', url: 'https://dribbble.com/shots/24071214', element: 'overall', localImagePath: `${IMG}/id8.png` },
  { id: 9, title: 'Football App - Settings & Alert Preferences UI', url: 'https://dribbble.com/shots/27249321', element: 'step-heads', localImagePath: `${IMG}/id9.png` },
  { id: 10, title: 'AI-Powered Productivity Dashboard - Aizen', url: 'https://dribbble.com/shots/26599212', element: 'step-heads', localImagePath: `${IMG}/id10.png` },
];
const UI = (args && args.ui) || 'a dark, warm "Almanac Noir" statusline-configurator web UI (warm near-black ground, bone text, single amber accent, ember alerts only, 2px radius, hairline rules; fonts Big Shoulders Display / IBM Plex Sans / JetBrains Mono). Static elements: a PWRL/Statusline/configurator masthead brand, three numbered section headers, and a terminal-window live-preview frame.';

if (!pool.length) { return { error: 'empty pool', survivors: [], matrix: [] }; }

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          id: { type: 'integer' },
          suitable: { type: 'boolean' },
          reason: { type: 'string' },
          informs: { type: 'string' },
        },
        required: ['id', 'suitable', 'reason', 'informs'],
      },
    },
  },
  required: ['verdicts'],
}

const candidateList = pool
  .map(c => `- id=${c.id} | "${c.title}" | element=${c.element} | VIEW IMAGE: ${c.localImagePath}`)
  .join('\n');

phase('Evaluate');
const evals = await parallel(SKILLS.map(skill => () =>
  agent(
    `You are a design specialist evaluating reference suitability through ONE lens only.\n\n` +
    `Step 1: invoke the "${skill}" skill via the Skill tool (one call) and FULLY ADOPT its guidance. Judge ONLY through ${skill}'s principles.\n\n` +
    `We are visually elevating this UI: ${UI}\n\n` +
    `Below are candidate Dribbble references. For EACH candidate, use the Read tool to VIEW its image at the given local path, then decide: by ${skill}'s principles, does this reference genuinely inform the HIERARCHY / LAYOUT / DENSITY / TYPOGRAPHY / BRAND-IDENTITY elevation of THIS dark instrument-panel configurator? Ignore color (it stays fixed). Set suitable=true ONLY for a genuine, on-brand, instrument-precise fit; reject anything bright / playful / light / consumer / generic / off-brand. Be discerning - a strict lens is the point.\n\n` +
    `Candidates:\n${candidateList}\n\n` +
    `Return one verdict object per candidate id (suitable, a one-line reason, and a short "informs" naming the specific pattern it would teach).`,
    { label: `eval:${skill}`, phase: 'Evaluate', schema: VERDICT_SCHEMA }
  ).then(r => ({ skill, verdicts: (r && r.verdicts) || [] }))
));

phase('Converge');
const bySkill = {};
for (const e of evals.filter(Boolean)) {
  bySkill[e.skill] = Object.fromEntries(e.verdicts.map(v => [v.id, v]));
}
const survivors = [];
const matrix = [];
for (const c of pool) {
  const votes = SKILLS.map(s => (bySkill[s] || {})[c.id]);
  const yes = votes.filter(v => v && v.suitable).length;
  matrix.push({
    id: c.id, title: c.title, url: c.url, element: c.element, agree: yes,
    votes: SKILLS.map((s, i) => ({ skill: s, suitable: !!(votes[i] && votes[i].suitable), reason: (votes[i] && votes[i].reason) || '(no verdict)' })),
  });
  if (yes === SKILLS.length) {
    survivors.push({
      id: c.id, title: c.title, url: c.url, element: c.element,
      informs: SKILLS.map((s, i) => `${s}: ${(votes[i] && (votes[i].informs || votes[i].reason)) || ''}`),
    });
  }
}
return { survivors, matrix, unanimousCount: survivors.length, poolSize: pool.length };
