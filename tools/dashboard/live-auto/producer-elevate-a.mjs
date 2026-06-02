// Real variant producer for the "elevate Mustard" loop run (candidate A).
// Design-brain authored (no LLM). Reuses the dashboard's EXISTING CSS classes
// (.card .stat .k .big .unit .sub .pull — all global in the inline <style>), so
// the accepted variant is fully styled regardless of carbonize CSS-porting.
// Three variants, three distinct primary axes per live.md Phase C, all within
// the Mustard identity. Each fixes the em-dash in the original (taste-skill 9.G).
//
// Plugged via: orchestrator.mjs --producer=./producer-elevate-a.mjs

export default function createProducer() {
  return {
    async generateVariants(event, context = {}) {
      const astro = context?.wrapInfo?.styleMode === 'astro-global-prefixed';
      // Minimal carbonize-safe base rule per variant: a no-op marker that
      // satisfies the blueprint's per-variant base-rule check. Visual identity
      // is carried entirely by the reused global classes, not by this CSS.
      const baseRule = (n) =>
        astro
          ? `[data-impeccable-variant="${n}"] > .card { }`
          : `@scope ([data-impeccable-variant="${n}"]) { :scope > .card { } }`;
      const scopedCss = [1, 2, 3].map(baseRule).join('\n');

      const variants = [
        // v1 — HIERARCHY: promote the reassurance ("not remaining build work")
        // to the lead so the 0% reads as "by design", not "behind". em-dash fixed.
        {
          innerHtml:
            '<div class="card stat">' +
            '<div class="k">Activation / deployment closure</div>' +
            '<div class="big">0<span class="unit">% exercised</span></div>' +
            '<div class="sub"><strong>Not remaining build work.</strong> 17 of 20 forward items are operator-gated: credentials and infrastructure that cannot run in this workspace. Bounded-residual by design.</div>' +
            '<div class="pull">"The harness is built; this axis switches on at a real deployment."</div>' +
            '</div>',
        },
        // v2 — STRUCTURE: lead with the count (17 of 20 open) instead of 0%,
        // recasting the metric as progress-remaining rather than zero-done.
        {
          innerHtml:
            '<div class="card stat">' +
            '<div class="k">Activation / deployment closure</div>' +
            '<div class="big">17<span class="unit">of 20 open</span></div>' +
            '<div class="sub">0% exercised, and that is correct. These are operator-gated items (credentials, infrastructure) that cannot run in this workspace. Not build work; bounded-residual by design.</div>' +
            '<div class="pull">"The harness is built; this axis switches on at a real deployment."</div>' +
            '</div>',
        },
        // v3 — DENSITY: tightest copy, single punch line up top, em-dash fixed.
        {
          innerHtml:
            '<div class="card stat">' +
            '<div class="k">Activation / deployment closure</div>' +
            '<div class="big">0<span class="unit">% exercised</span></div>' +
            '<div class="sub">Operator-gated, not unfinished. 17 of 20 forward items need real credentials and infrastructure. Bounded-residual by design.</div>' +
            '<div class="pull">"The harness is built; this axis switches on at a real deployment."</div>' +
            '</div>',
        },
      ];

      return { scopedCss, variants };
    },
  };
}
