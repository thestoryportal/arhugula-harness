// Loop plan for the "elevate Mustard" run (candidate A).
// One contained, carbonize-safe move: re-hierarchy the activation/deployment
// stat card (disambiguated from the sibling build-closure card by --text).
// outerHTML is the REAL element (with its .k/.big/.sub/.pull children) so the
// skill-chaining producer elevates the actual card, not a skeletal stub.
export default [
  {
    classes: 'card,stat',
    tag: 'div',
    text: 'Activation / deployment closure',
    action: 'polish',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
    outerHTML:
      '<div class="card stat">' +
      '<div class="k">Activation / deployment closure</div>' +
      '<div class="big">0<span class="unit">% exercised</span></div>' +
      '<div class="sub"><strong>17 of 20</strong> forward items open. This is <strong>not remaining build work</strong> - it is operator-gated (credentials + infrastructure that cannot run in this workspace) and bounded-residual by design.</div>' +
      '<div class="pull">"The harness is built; this axis switches on at a real deployment."</div>' +
      '</div>',
  },
];
