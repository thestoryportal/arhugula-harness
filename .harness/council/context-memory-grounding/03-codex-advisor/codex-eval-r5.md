# Codex evaluation — Round 5 (evidence-enrichment) · Stage E3 (out-of-family half)

> Out-of-family reviewer **gpt-5.5** via `codex review` (ChatGPT subscription, $0, `env -u OPENAI_API_KEY … -c preferred_auth_method="chatgpt"` — subscription-safe, no metered fallback) · 2026-06-04. Fed the **research primer only** (descriptive, no Claude-family conclusions — decorrelation discipline); reviewed the plan + raw research **cold** (adversarial findings + advisor eval deliberately withheld). Prompt: `$CLAUDE_JOB_DIR/tmp/codex_prompt.txt`; full transcript: `$CLAUDE_JOB_DIR/tmp/codex_out.txt` (274 KB).

---

## Verdict: **SOUND-WITH-FIXES**

> "The council mostly resolved proportionality-vs-canon well, but the acceptance gate is still vulnerable to rare-class false-green results and a few concrete, already-observed memory-store risks were deferred too far."

No P0 (nothing blocking). 5 findings: 1× P1, 3× P2, 1× P3.

## Findings (verbatim)

- **[P1] Add a non-vacuous exposure floor for D4/D6** (DELIBERATION-2 §"Residuals" / WS-0 pass condition):
  > The base-rate rule prevents a zero-zero class from counting as the required improvement, but the plan can still pass if D4/D6 are unexercised while another class improves. Since the MVP introduces D4/D6-sensitive surfaces (`superseded_by`, recovery pointers, instruction conflicts), the WS-0 gate should require minimum exposure or explicitly mark the result incomplete rather than SOUND when those classes are not tested.

- **[P2] Carry degree-keyed tiering into WS-3a** (MVP-3 / WS-3a):
  > Refusing an episodic/semantic directory split is proportionate, but the final MVP does not preserve the empirical degree-based rule that the evidence says should drive compaction: pin in-degree ≥5, keep linked 1–4, and archive/JIT the 39 zero-inbound notes. Without that rule in WS-3a, downstream compaction can still miss the counted bloat/load-bearing boundary and make the same prefix/category mistakes the corpus analysis warns against.

- **[P2] Promote already-triggered consolidation hygiene** (consolidation deferral):
  > The deferred consolidation trigger is `≥4-ref-unwritten` patterns, but the evidence already found two such patterns at 5× and 4× references and calls them actionable now. Deferring the whole consolidation pass either makes the trigger fire immediately in the execution arc or leaves a known D4 surface unresolved; make the two-note one-time promotion MVP hygiene and keep only the recurring consolidation mechanism deferred.

- **[P2] Gate standing recovery pointers before relying on them** (G-LINK deferral / X-min):
  > Keeping full G-LINK trigger-gated is reasonable for hand-authored episodic links, but bare MVP still relies on standing machine-managed references such as the reinject pointer, and the evidence says cross-store kebab/underscore drift is live at HEAD. A minimal resolver check for standing recovery/supersede pointers should be MVP-now; otherwise D5 recovery can silently fail before an observed D4 promotes the full link gate.

- **[P3] Derive L1 assertions from live invariants** (MVP-6 / WS-1 L1):
  > The deep-dive used the `[i]` citation check as an example of an L1 assertion, but this plan promotes that example into MVP without showing it is a live harness invariant tied to D1–D6. Keep the deterministic pre-eviction check, but scope it to invariants discovered by the WS-1 dependency scan rather than hard-coding an evidence-corpus example as a work item.

---

## Three-way convergence / divergence analysis (the E3 signal — per advisor's "weight where Codex disagrees")

| Topic | Adversarial (Claude-family) | Advisor (Claude-family) | Codex (OUT-of-family) | Disposition |
|---|---|---|---|---|
| **WS-0 rare-class vulnerability (D4/D6)** | F2-03: name D6 blindness; **annotate-not-floor** | flagged the under-pressed "is the gate even run / minimum-viable-gate floor" | **[P1] annotate is NOT enough** — plan can pass on other classes while D4/D6 untested → **require minimum exposure OR mark result incomplete** | **CONVERGENCE on the risk; DIVERGENCE on the fix.** The decisive find — all 3 reviewers point here; Codex (cold) pushes past annotate to an exposure-floor/incomplete-marking. → **E3b must resolve.** |
| **Standing recovery/supersede pointer** | F2-01: **dormant-G-LINK fine** + name the existing `[ -f ]` self-check | (not pressed) | **[P2] minimal resolver MVP-now** — the `[ -f ]` guard handles *absence*, not *cross-store drift* (live at HEAD) → D5 can silently fail | **DIVERGENCE.** Codex distinguishes graceful-degrade-on-absence from resolution-validation. → **E3b must resolve** (C9/C5/C3). |
| **Degree-keyed tiering** | (not flagged) | (not flagged) | **[P2] carry the explicit rule into WS-3a** (pin ≥5 / keep 1–4 / archive 39 zero-inbound) | **Codex-UNIQUE.** The council had the data (EVID F1/F3) but left it citation-enriching, not operationalized in WS-3a MVP. → **E3b: C3/C2.** |
| **Already-triggered consolidation** | (not flagged) | (not flagged) | **[P2] the 2 ≥4-ref patterns are actionable NOW** → make the one-time promotion MVP hygiene; keep only the recurring mechanism deferred | **Codex-UNIQUE.** Sharpens C1/C3's "one-time hygiene, not a standing WS" — the trigger is already met. → **E3b: C1/C3.** |
| **L1 assertion scoping** | (folded F2 into WS-1) | (noted L1 fine) | **[P3] scope L1 to WS-1-dependency-scan invariants**, not the hard-coded `[i]` example | **Codex-sharpen.** → **E3b: C2/C5/C8.** |

**Net:** Codex genuinely earned its keep — 3 P2 findings the two Claude-family reviewers did **not** surface (degree-tiering-into-WS-3a; already-triggered-consolidation-MVP; standing-pointer-resolver-MVP) + a P1 that **diverges on the fix** for the one risk all three saw. The out-of-family read paid off exactly where the advisor predicted (the WS-0 gate's framing blind-spot) and beyond it.
