# E2 — Adversarial review of the B-116 reconciled council position (2026-08-07)

*(Filed verbatim from the genuine harness-adversarial-reviewer invocation; verdict line at end.)*

**Scope:** charter + filing §1–§7 + all six ledger contributions (A1-c9, A1-c11, A2-c1, A2-c7, B-c9-crossread, B-c11-crossread), attacked at HEAD.

## F-01 — Member #1 is NOT provider-attested at ANY raise site; the ratified predicate demotes it *(decided)*
- **§2.7.6 Class 1 (HALT — the reconciled table's premise is false) · §4.1 Class 2**
- `LLMDispatchProviderUnreachableError` has exactly three raise sites, all harness-side registry lookups that never contact a provider: `llm_dispatch.py:1525` (`provider_name not in self.providers`), `:1549` (`_PROVIDER_OPERATIONS.get(...) is None`, "Defensive — every key … constructed at stage 3a per C-RT-05"), `:1865` (terminal else of the provider-arm chain). Class docstring `:184-193`: "resolves to a provider absent from `ctx.providers`". The name says "Unreachable"; the semantics are "unregistered".
- C9's own rationale ("a half-open probe can only re-test an assertion the provider makes") disqualifies it: a half-open trial re-executes the same in-process registry lookup against a map built once at bootstrap — re-fails identically for the process lifetime. #1 is MORE disqualified than the conceded #5, and candidate-independent within a provider (Probe-B/C harm, unmitigated).
- Resolution: re-adjudicate row 1 under the predicate BEFORE the ratification AUQ; the review does not supply the disposition.

## F-02 — Member #2 is heterogeneous: 3 pre-flight raise sites vs 25 response-parsing sites; a type-level guard cannot express the predicate *(decided)*
- **§2.7.6 Class 2 · §4.1 Class 2** — discharges the re-verification C9 registered.
- 28 `raise LLMDispatchPayloadShapeError` sites in `llm_dispatch.py`. Harness pre-flight, before provider contact (3): `:323` `_coerce_payload(step.step_payload)` (coercion of the harness's own OUTGOING payload; docstring `:201-211`), `:1266` post-join-synthesis effect-free tool-binding guard ("before the provider call"), `:3507` external-CLI text-only rejection. Provider-response parsing after the call (25): `:3634/:3682` Anthropic, `:4184–:4316` OpenAI, `:4844–:4965` Ollama, `:5108/:5142` external-CLI.
- Reachability: `retry_breaker_fallback.py:983` → `RuntimeLLMDispatcher.dispatch` (`:1167`) contains `:1244`/`:1266` — a mis-shaped `step.step_payload`, identical for every candidate, reaches `:1028` and charges every breaker in the chain: B-116's own Probe-B/C harm live inside a member all six voices keep counting.
- The ratified "type tuple of three, ~6 src lines" guard cannot split `:323` from `:4844`. C9's own falsifier of his A1 #5 position ("a type-level guard cannot express 'sometimes'") applies verbatim to #2 and was not applied.
- Resolution: the ratification package must state whether #2 is dispositioned whole (which side) or split at the raise site, and by what mechanism.

## F-03 — t3's cost is mispriced and mischaracterized; it is a load-bearing condition on two voices' sign-off *(decided)*
- **§2.7.6 Class 2 · §4.1 Class 2 (brushes (b) — amends a P5-CK-cleared sibling contract)**
- `Spec_Operational_Discipline_v1_2.md:511-530` — C-OD-09 §9.2's own 18-row table does NOT contain `fallback.exhausted`; `sampling_mode.py` is byte-exact conformant to its owning contract. The divergence is CP §3.5 vs OD §9.2 — a two-SPEC disagreement whose resolution direction (OD up to 19, or CP down) is itself unratified. Pinning it EXTENDS a floor whose §9.3 invariant reads "inviolable" (`:538`) — what C11's justification denies.
- Pricing: four fixture sites move, not two (`test_sampling_mode.py:93`, `:98`, `:24`; `test_composite_sampler.py:55` + `_LITERAL_ALWAYS_SAMPLED` at `:29`).
- Both primaries' positions are conditional on t3 (C9: no-replacement-counter survives "only with your floor term attached"; C11: "Without it, it does not"). Ratifying (II) with t3 out-of-venue leaves the position resting on an unmet condition.
- Resolution: surface t3 as a separately-scoped cross-axis spec amendment with its own clearance marker; state what the C9/C11 positions become if deferred.

## F-04 — t2's span placement is an unresolved C7⊥C11 conflict presented as settled *(decided)*
- **§2.7.6 Class 3 · §4.1 Class 1** — C7 ruled the outer `retry.skipped`-class surface; C11 showed the non-charged path is the INNER attempt span (`:1022-1028`) vs the pre-check outer (`:675-681`) and left "whichever span, carries the candidate key". Name the emitting span in the term or record it as an impl-leg open item.

## F-05 — #6's conditionality silently stripped; B-115 sequencing circular *(decided)*
- **§2.7.6 Class 3 · §4.1 Class 1** — C9's row 6 is "don't count — conditionally … provided B-115's build confirms deterministic; if racy → C5 retry-classification fix, not breaker counting" [MODERATE]; the reconciled table flattens it. And the sequencing (ratify B-116 → build B-115) defers the very verification the disposition assumes. Carry the conditional verbatim with the falsifier as a named revisit-trigger.

## F-06 — "provider-attested" is realized in code as a `.status_code` duck-type, not a provenance test *(proposing)*
- **§2.7.6 Class 3 · §4.1 Class 1** — `:368-370` tests `getattr(exc,"status_code",None) in (401,403)` on ANY exception; no harness type carries `.status_code` at HEAD (latent, not live). The predicate's stated FORM and its RATIONALE (the half-open recovery-model test) come apart exactly at F-01/F-02 — the rationale is what adjudicates all rows correctly. Consider recording the recovery-model rationale as the normative test, with "provider-attested" as shorthand.

## F-07 — Nobody named that the other two `record_failure` sites are untouched *(decided; strengthens the position)*
- **§2.7.6 Class 3 · §4.1 Class 1** — `:1072` (max-attempts) and `:1091` (staircase escalation) are outside the fail-fast branch: genuine transient provider unhealth (network/429/5xx → TRANSIENT_RETRY `:355-357`) reaches the breaker there, unaffected under either reading. Bounds both C9's and C11's "strongest argument against"; its absence overstates (II)'s cost.

## F-08 — §9.2 floor addition's telemetry-volume cost at multi-tenant unpriced *(proposing)*
- **§2.7.6 Class 3 · §4.1 Class 1** — always-sampled = head 1.0 at every cell incl. multi_tenant (base 0.2). Register as a row on t3.

## Cite verification — all five load-bearing NEW cross-read claims VERIFIED at HEAD
(a) `retry_breaker.py:459-461` tool_id breaker-key default — VERIFIED (C7's "never populated" falsified; C9's flag-CONFLICT stands). (b) `attempt_half_open()` zero production call sites — VERIFIED. (c) `sampling_mode.py:119-140` 18 members, `fallback.exhausted` absent — VERIFIED (C7's `:118-139` is one-line drift; C11 correct). (d) C-CP-03 §3.3 zero-charge advance — VERIFIED byte-exact. (e) `workflow_driver.py:5564-5572` first-failed-step termination — VERIFIED. **No phantom cites found.**

## Rejected candidates (transparency)
Framing contamination (clean); X-AL-3 (no violation — t2 routed via attribute-owner authority, t3 named as amendment); waiver-attribute security (structural, no content); uncertainty tags (honestly placed); FM-H (all findings anchor to file:line); HITL t5 (sound); `retry.*` cardinality pin (verified; refusal correct); `capability_shortfall` homonym refusal (verified); Probe-D re-pin (priced); t4 persistence pin (no breaker_state table wired; correctly forward-conditional).

## Disposition
F-01 is the halt: the table is wrong at the top, not the margin. F-02 answers the registered re-verification "both". F-03 makes two sign-offs conditional on an out-of-venue amendment. The reconciled READING (II) is not disturbed — F-01/F-02 push toward it, F-07 weakens the counter-argument. Recommend: bounded council re-adjudication of rows 1–2 under the ratified predicate, re-scope t3, re-issue before the AUQ.

`E2: 8 findings — §2.7.6: 1×Class 1 (F-01), 2×Class 2 (F-02, F-03), 5×Class 3 (F-04..F-08) · §4.1: 3×Class 2, 5×Class 1`
