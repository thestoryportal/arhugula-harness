/**
 * Smoke-test plan: 2 autonomous moves against _smoke/seed.html.
 *
 * Each move = selector hints + action + which variant to accept. The
 * orchestrator resolves the hints against the on-disk file (recovering tag +
 * text), POSTs a `generate` event, waits for the canned producer to write 3
 * variants, POSTs an `accept`, and waits for carbonize cleanup.
 *
 * Move 1 targets the <h1> hero (accept variant 2 — the "bolder" weight).
 * Move 2 targets the <a> CTA (accept variant 1 — the color variant), proving
 * the loop runs over a different tag without the h1-hardcoding the e2e fixture
 * agent has.
 */
export default [
  {
    elementId: 'hero',
    classes: 'hero-title',
    tag: 'h1',
    action: 'bolder',
    freeformPrompt: 'make the hero command the eye',
    count: 3,
    acceptVariant: 2,
    pageUrl: '/',
  },
  {
    elementId: 'cta',
    classes: 'cta',
    tag: 'a',
    action: 'colorize',
    count: 3,
    acceptVariant: 1,
    pageUrl: '/',
  },
];
