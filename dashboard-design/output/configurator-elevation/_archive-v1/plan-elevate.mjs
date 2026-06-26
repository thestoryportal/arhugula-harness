// Real 4-skill elevation plan for the Powerline statusline configurator UI.
// Each move targets a STATIC, loop-elevatable element of the configurator shell
// (the app.js-rendered controls under #display/#lines/#custom are out of scope).
// The producer (producer-skillchain.mjs) invokes impeccable + design-taste-frontend
// + ui-ux-pro-max + frontend-design, then authors `count` in-identity variants
// reusing the existing CSS classes (carbonize-safe; no new CSS). acceptVariant=1
// persists the producer's primary (hierarchy-axis) variant per move.
//
// outerHTML is the REAL element from ~/.claude/powerline-config/static/index.html
// so the skill chain elevates the actual markup, not a stub. Em-dashes in the
// source copy are converted to hyphens by the producer's taste-lint gate.
export default [
  // 1 - masthead brand / product identity
  {
    classes: 'brand',
    tag: 'div',
    text: 'Statusline',
    action: 'typeset',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="brand">' +
      '<span class="mark">PWRL</span>' +
      '<span>Status<span class="sig">line</span></span>' +
      '<span class="sub">configurator</span>' +
      '</div>',
  },
  // 2 - step 1 head: Theme & display
  {
    classes: 'step-head',
    tag: 'div',
    text: 'Theme & display',
    action: 'polish',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="step-head"><span class="num">1</span>' +
      '<div><h2>Theme &amp; display</h2><p>Overall look - style, theme, wrapping.</p></div>' +
      '</div>',
  },
  // 3 - step 2 head: Segments
  {
    classes: 'step-head',
    tag: 'div',
    text: 'Hover a name',
    action: 'polish',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="step-head"><span class="num">2</span>' +
      '<div><h2>Segments</h2><p>Per line: toggle, reorder, set options. Hover a name for what it shows. Budgets &amp; limits live with their segment.</p></div>' +
      '</div>',
  },
  // 4 - step 3 head: Custom data
  {
    classes: 'step-head',
    tag: 'div',
    text: 'Custom data',
    action: 'polish',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="step-head"><span class="num">3</span>' +
      '<div><h2>Custom data</h2><p>Extra segments appended after powerline (stored in the settings.json command).</p></div>' +
      '</div>',
  },
  // 5 - preview caption (secondary text)
  {
    classes: 'approx',
    tag: 'div',
    text: 'Approximate',
    action: 'quieter',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="approx">Approximate - rendered from sample session data with your installed nerd font.</div>',
  },
];
