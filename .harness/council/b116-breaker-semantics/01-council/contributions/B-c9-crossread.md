# B — C9 (Reliability & Recovery) cross-read debate contribution — B-116 (verbatim, 2026-08-07)

**I re-grounded @C1's §3.3 falsification myself before answering. It holds — and my own re-grounding produced two further falsifiers @C1 did not have. I concede member #5.**

## What I verified this session (Read only)

1. **C-CP-03 §3.3 is byte-exact as @C1 cites it** (`Spec_Control_Plane_v1_2.md:373-387`). The `on_capability_shortfall` procedure block contains **three steps and no breaker charge**; §3.4 (`:391`) is the *adjacent* section that attaches breakers per-`{provider, model}`. [HIGH]
2. **The code matches.** The capability-shortfall pre-check advances at `retry_breaker_fallback.py:650` and `continue`s — **the breaker object is not even fetched until `:662-665`, one step later.** So the shortfall path cannot charge a counter it never obtains. Capability shortfall **is** candidate-discriminating (a fact about that model's capability profile) and charges **zero**. **My "candidate-discriminating ⇒ count" inference is falsified as a sufficient condition.** [HIGH]
3. **`llm_dispatch.py:4362-4383` reads as @C1 describes**, and better for his case than either of us said: `:4380-4383` refuses on `scope_ref != memory_context.scope_ref` — an equality against **the harness's own context value**. [HIGH]

## SEAM #5 — I was wrong, and the decisive evidence is in my own predicate

Three grounds, in ascending order of force. **(a)** does *not* rescue me — the pre-dispatch/runtime-observation distinction the prompt offers is a distinction without a difference **for the counting question**, because the counter's subject is *whose assertion the fault is*, not *when it was learned*. §3.3 is learned pre-dispatch and #5 at runtime; both are adjudicated by harness code, and neither is a claim the provider made.

1. **@C1's falsifier stands** (verified above). The shipped predicate has a second conjunct: *provider-attested*.
2. **The type's own contract text falsifies my model-degradation reading.** C-MEM-19 v1.3 defines `MemoryToolExecutionInputError` as *"a refusal of **caller- or model-supplied** arguments"* (`memory_tool_executor.py:154-156` — note `harness_runtime/`, **not** `lifecycle/`; my A1 path was loose). **Caller-OR-model.** The guard is necessarily a **type-level** predicate, and at type level #5 does not discriminate a degraded model from a bad caller. My A1 read the type as model-scoped. It is not.
3. **The model-supplied half itself contains a candidate-independent sub-shape.** `:4380-4383` refuses on mismatch against harness-held state. A harness carrying a `scope_ref` the model was never given yields an **identical refusal from every candidate** — Probe C's exact shape, on the very member I wanted to count. **My own rule returns "sometimes" for #5, and a type-level guard cannot express "sometimes."**

**The concession improves the fix rather than costing it, and it answers @C11's strongest counter-argument.** @C11's honest fear is the hand-maintained allowlist drifting. My A1 split would have left "two of three `MemoryTool*` types charge, one doesn't" — a per-type judgment that drifts on the next re-typing (B-41/B-84/B-88/B-114 already re-typed this family four times). Conceding yields a rule a reviewer can check in one line: **no `MemoryTool*` exception charges the provider-model breaker, because none is provider-attested.**

**Self-correction, stated so it cannot be carried stale:** my A1 refinement 1 claimed the guard "collapses to a two-type tuple." **That is now false by my own concession** — it is `MemoryToolExecutionInternalError`, `MemoryToolExecutionInputError`, plus B-115's type later. Three, not two.

## Engaging the peers by name

**@C1 — COHERE on the predicate, and I supply the mechanism argument it was missing.** "Provider-attested ∧ discriminating" is derived from precedent; my domain supplies why it is *correct* rather than merely *shipped*: **a half-open probe can only re-test an assertion the provider makes.** It cannot re-test a harness adjudication — the trial re-executes the same harness code and re-opens. Provider-attestation is precisely the property that makes the breaker's **recovery model** applicable. That is a C9-domain reason, and it is stronger than the precedent alone.

**@C1 — refine on the fall-through home.** Verified: `FallThroughCause` is closed at 4, values byte-exact to §3.5, and its `CAPABILITY_SHORTFALL` carries the same sense as the breaker enum's (`fall_through_procedure.py:64-65` vs `harness_breaker_schema.py:141-143`). Your placement is right, but be honest about what it gives my domain: a **registered home, not a live signal**. I accept that trade only because the alternative live signal is a corrupted counter.

**@C7 — flag-CONFLICT, narrow but load-bearing.** Your `tool_id` offer was **predicated on #5 tripping**. With #5 conceded there is **no #5 trip**, so populating `tool_id` on it is vacuous. Your ruling still closes my FM-Q for `#1/#2/#3` trips — real, and still owed — but **it is no longer compensation for #5.** Do not let the ledger record it as such.

**@C11 — COHERE on outcome, flag-CONFLICT on rationale.** You reached don't-count via *"same nature"* + harness-internal-by-construction. **That premise is falsified at HEAD**: #5 is *not* harness-internal by the C-MEM-19 type boundary — the boundary explicitly keeps it as the argument-refusal case (`memory_tool_executor.py:193-195`). Right disposition, wrong reason. If the §14.6 amendment records your rationale, it encodes a falsified fact and becomes stale-carry on the next re-typing. **The amendment must record @C1's predicate, not "same nature as #4."** Your (a) — non-counted fault stays on the terminal verbatim — I CONFIRM, and it now binds #5 too.

## The three confirm-or-refine items

**(A) @C1's falsification of my unbounded-traversal counter-argument — CONCEDED, verified.** `workflow_driver.py:5564-5572` returns `RunStatus.FAILED` with `terminal_step_index` on the first failed step. For a candidate-independent fault the bound is **one step per run**. Your second half also lands: breaker state is in-memory per-process, so (I) does not bound cross-run repetition either. **Two revisit-triggers, named jointly so neither is lost:** (i) a candidate-independent fault class admitted to the fail-fast branch *after* a paid provider call (mine); (ii) any topology that re-dispatches a failed step *within* a run (yours — the bound is a property of the driver's terminality, not of the breaker).

**(B) @C7's sampling-floor term — ACCEPTED AS BINDING, and it changes my recommendation 6.** You are right that I priced "correct-and-thin" at `solo × local` where base rate is 1.0. At `team × self-hosted` (0.1) the residual is dropped nine times in ten, and **correct-and-absent is not a reliability posture.** So: **my "no replacement counter" recommendation survives only with your floor term attached.** Bind them in the amendment. Without the floor guarantee I would have to reopen the replacement-counter question — which is exactly the over-engineering I want to avoid, so the cheap term buys the expensive one off.

**(C) @C7's refusal of the `capability_shortfall` reuse — CONFIRMED without reservation.** I surfaced the collision; I did not request the value (A1 rec 5). Your homonym grounds are the attribute-owner's call. Adding my own re-grounding: both enums bind the token to the *cross-family exhaustion* sense, so reuse would collide in two namespaces, not one. **And with #5 conceded the collision is moot for this leg** — no #5 trip, no cause needed. It survives only as a forward row.

## Registered for the E2 adversarial leg (not a reopened disposition)

Adopting "provider-attested" as the predicate creates an obligation nobody has discharged: **`#2 LLMDispatchPayloadShapeError` must be re-verified against it.** If that type is raised by harness-side *pre-flight* validation of an outgoing payload rather than by a provider rejection, the predicate demotes it too. All four voices and the filing's §5 have it COUNT; I keep it COUNT and register the check rather than assert past it. [MODERATE]

Witness consequence: my A1 rec 2 stands (do not assert a half-open path — `attempt_half_open()` has zero production call sites). Add: the #5 witness must assert `fail_count == 0` across all chain breakers for `MemoryToolExecutionInputError`, **and** — per @C11 (a) — that `last_failure_detail` still carries the type name and message.

## Final per-member table (C9, post-cross-read)

| # | Member | C9 FINAL | Basis |
|---|---|---|---|
| 1 | `LLMDispatchProviderUnreachableError` | **count** | Provider-attested and endpoint-local; the only class whose half-open recovery model is applicable. Unchanged. |
| 2 | `LLMDispatchPayloadShapeError` | **count** | Provider-boundary rejection. Unchanged — with the predicate-conformance re-verification registered for E2 above. |
| 3 | `.status_code ∈ {401,403}` duck-type | **count** | Provider-attested credential fact; a half-open probe genuinely re-tests it after rotation. Unchanged. |
| 4 | `MemoryToolExecutionInternalError` | **don't count** | Harness-internal by the C-MEM-19 v1.3 type boundary; candidate-independent by construction. Unchanged. |
| 5 | `MemoryToolExecutionInputError` | **don't count — CHANGED from my A1** | Not provider-attested (`llm_dispatch.py:4376-4383` is harness adjudication); type text is *"caller- or model-supplied"*, so it does not discriminate at type level; and its mismatch sub-shape is candidate-independent. |
| 6 | *prospective* B-115 (b′) ledger-idempotency conflict | **don't count — conditionally** | Candidate-independent state fact; conditional on B-115's build confirming determinism. If racy, the fix is its retry classification (C5's surface), not the counter. Unchanged. [MODERATE] |

**Guard predicate, final:** charge the provider-model breaker **only** on a fault the provider itself asserted. Realized as a type tuple of three (two today, plus B-115's later), on `record_failure` **only**, ~6 src lines at `retry_breaker_fallback.py:1016-1028`.

SEAM-#5: DON'T-COUNT
