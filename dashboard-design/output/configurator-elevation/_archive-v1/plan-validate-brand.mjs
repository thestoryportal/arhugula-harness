// Single-move validation of the GENUINE skillchain producer (one paid claude
// spawn). Confirms: claude CLI authenticates, SKILLCHAIN_WS skill-resolution
// works, all 4 skills fire (proof captured in stream-json), variant JSON parses,
// accept + carbonize scrub clean. Elevates the masthead brand - kept if good.
export default [
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
];
