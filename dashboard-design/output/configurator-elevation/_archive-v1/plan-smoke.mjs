// No-LLM smoke plan for the configurator elevation loop.
// One move targeting the "Segments" step-head, disambiguated by --text from the
// two sibling step-heads (same .step-head class). Validates: wrap accepts this
// file, selector resolution by class+tag+text works, accept + carbonize scrub
// runs clean. Run with the DEFAULT canned producer (no LLM, $0).
export default [
  {
    classes: 'step-head',
    tag: 'div',
    text: 'Hover a name',
    action: 'polish',
    count: 2,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="step-head"><span class="num">2</span>' +
      '<div><h2>Segments</h2><p>Per line: toggle, reorder, set options. Hover a name for what it shows. Budgets &amp; limits live with their segment.</p></div>' +
      '</div>',
  },
];
