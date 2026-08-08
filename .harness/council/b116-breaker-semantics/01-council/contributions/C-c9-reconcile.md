# E2b — C9 (Reliability & Recovery) RECONCILE contribution — B-116 (2026-08-07, verbatim)

**I re-verified F-01 and F-02 at the raise sites myself before responding. Both hold. I ACCEPT F-01, F-02, F-05, F-06 and F-07. Two of my own carried positions are falsified by that verification — row #1 (which I authored and carried unchanged through cross-read) and my "~6 src lines" pricing. I state both as corrections, not as softenings.**

## What I verified this session (Read only, at HEAD)

1. **All three `LLMDispatchProviderUnreachableError` raise sites are harness-side.** `:1525` `provider_name not in self.providers` (in-process dict membership); `:1549` `_PROVIDER_OPERATIONS.get(...) is None`, comment `:1546-1548` "Defensive — every key in self.providers is one of the three constructed at stage 3a per C-RT-05"; `:1865` the terminal `else` of the `isinstance` adapter-arm chain. Class docstring `:184-193`: "resolves to a provider absent from `ctx.providers`". **No site contacts a provider.** [HIGH]
2. **28 `raise LLMDispatchPayloadShapeError` sites, partitioned exactly as E2 states.** Pre-flight 3 — `:323` (`_coerce_payload`, Pydantic-validating the harness's OWN outgoing `step.step_payload`), `:1266` (post-join tool-binding guard, "before the provider call"), `:3507` (external-CLI text-only, "before the subprocess boundary"). Response-parsing 25 — `:3634/:3682`, `:4184–:4316`, `:4844–:4965`, `:5108/:5142`. [HIGH]
3. **F-02's reachability holds.** `:1244 payload = _coerce_payload(step.step_payload)` sits inside `dispatch`, reached from `retry_breaker_fallback.py:983`. One mis-shaped `step.step_payload` — identical for every candidate — reaches `:1028` and charges **every breaker in the chain**. [HIGH]
4. **F-07 verified, and it is the load-bearing fact of this round.** `_classify_provider_exception` `:352-356/:371`: all other `Exception` subclasses → `TRANSIENT_RETRY` ("treat as network / rate-limit / 5xx until proven otherwise"). Transient → staircase `:1042` → charge at **`:1072`** (max-attempts) or **`:1091`** (escalation), with `breaker_cause` ∈ RATE_LIMIT / AUTH_FAILURE / FIVE_XX_STREAK (`:404-413`). Both sites are **outside** the fail-fast branch B-116 touches. [HIGH]

## F-01 — ACCEPT. Row #1 DEMOTED to don't-count.

Under the rationale form — *what does a half-open probe re-test?* — a trial call re-executes an in-process dict built once at bootstrap. It re-fails identically for the process lifetime. **#1 is more disqualified than the #5 I already conceded.** The one thing that could rescue it — candidate-discrimination at provider granularity — was falsified as a sufficient condition in my own cross-read by C-CP-03 §3.3. **This is a defect I authored** — my A1 row 1 came from the type's **name**, not its raise sites; the name is the defect vector and it caught all four voices and the filing's §5.

**What now protects against a provider being genuinely down — re-grounded, and the answer costs the demotion nothing.** A genuinely unreachable endpoint never travels as `…ProviderUnreachableError` (registry-miss only). A real network fault raises the provider SDK's own exception, propagates untouched, carries no `.status_code`, falls to the catch-all → `TRANSIENT_RETRY` → staircase → **`:1072`/`:1091`, where the breaker is charged at full strength**. Provider-down protection lives entirely on the transient path and is **untouched by B-116 under either reading**. Demoting #1 *purifies* the detector. [HIGH]

**Rename/re-type row: REGISTER, do not price into B-116.** "Unreachable" meaning "unregistered" has demonstrably misled this council, but the type maps to `RT-FAIL-PROVIDER-UNREACHABLE` per C-RT-14 (`:189-190`) carried in two cleared specs — Class 2 back-flow; the taxonomy token is C5/C7/OD's to author. The demotion stands on raise-site evidence regardless. [HIGH]

## F-02 — ACCEPT. Row #2 SPLITS. My "type tuple of three / ~6 src lines" is falsified.

Whole is wrong in both directions: whole-count ratifies the live `:323` chain-wide charge; whole-don't-count blinds the breaker to 25 provider-response degradation sites — the largest genuine model-instance-degradation class in the fail-fast branch, precisely what Pillar 4 says the per-model breaker is for. My own falsifier ("a type-level guard cannot express 'sometimes'") applies verbatim to #2 and I did not apply it. [HIGH]

**Mechanism: re-type the 3 pre-flight sites to a harness-internal sibling, per the B-88/A-ii precedent** ("C-MEM-19 v1.3 makes the failure-class boundary a TYPE boundary wherever the class is keyed on the raised exception type", `memory_tool_executor.py:184-236`). A-ii's shape constraints carry over: the new type must NOT subclass `LLMDispatchPayloadShapeError` (isinstance is subclass-inclusive), must not be a family base, and **must be admitted by name to the fail-fast tuple** — without that the 3 sites fall to the catch-all, retry a deterministic harness fault, then charge at `:1072` anyway. Strictly worse. [HIGH]

**Corrected guard shape.** Charge at `:1028` conditional on a negative predicate over a harness-internal tuple of **four** today — `MemoryToolExecutionInternalError`, `MemoryToolExecutionInputError`, `LLMDispatchProviderUnreachableError` (per F-01), `LLMDispatchPayloadShapeInternalError` (new, per F-02) — plus B-115's fifth **only on confirmed determinism** (F-05). **Honest line count: ≈30-35 src lines across two files — a 5x under-price in my cross-read, which I own.** Impl leg owes: enumeration of which of the 15 `pytest.raises(…PayloadShapeError)` catch sites target the three pre-flight raises [MODERATE]; and a **raise-site partition witness** (enumerates raise sites by type, asserts the pre-flight/response split) so a new raise on the wrong type fails a test rather than drifting silently — required, because A-ii itself missed a seventh site that B-114 had to repair. [MODERATE]

## F-05 — ACCEPT. Conditional restored verbatim.

> **DON'T count — conditionally.** Candidate-independent state fact, same as #4 — *provided B-115's build confirms it is deterministic; if it turns out racy, the correct fix is its retry classification (C5's surface), not breaker counting, and it should not be in the fail-fast branch at all.* [MODERATE]

**Named revisit-trigger:** if B-115's build shows the conflict is racy, row #6's disposition is VOID and the fault routes to C5 retry-classification. **B-115's type ships in the tuple only after B-115 confirms determinism — never speculatively.** The guard ships at four members; row #6 does not close with B-116.

## F-06 — YES: the recovery-model rationale becomes the NORMATIVE test.

**Normative test for the §14.6 amendment: *a fault charges the provider-model breaker only if a half-open trial call could return a different result than the trip did, for a reason attributable to the {provider, model} the breaker is keyed to*; "provider-attested" is recorded as shorthand, and the recovery-model test governs where they diverge.** Caveat carried plainly: the test is stated over a path with zero production call sites (`attempt_half_open()`) — this does not void it (OD §7.1 already contracts the transition) but **raises my A1 rec 3 (wire the dead half-open latch) to the highest-priority forward row**, because §14.6's own normative test now depends on it. [HIGH]

## F-07 — FOLDED IN. My "strongest argument against" is retired as decision-relevant.

Its premise is false in both directions: (i) driver terminality bounds the harm to one step per run (conceded in cross-read); (ii) the budget is not removed — `:1072`/`:1091` are outside the branch and genuine provider unhealth reaches the breaker there at full strength under either reading. What survives: N pre-checks + N span events per dispatch, within one step, once per run. Revisit-triggers kept: (i) a candidate-independent class admitted to fail-fast AFTER a paid provider call; (ii) any topology that re-dispatches a failed step within a run; **(iii) NEW — any change admitting a provider-attested class to the fail-fast tuple, which removes its retry staircase and lands its breaker charge after 1 failure instead of max_attempts — an effective 3x threshold tightening for that class.** [MODERATE]

## FINAL corrected per-member table (C9, post-E2b)

Test column: *could a half-open trial call return a different result, attributably to the {provider, model} the breaker is keyed to?*

| # | Member | Disposition | Recovery-model test | Conf |
|---|---|---|---|---|
| 1 | `LLMDispatchProviderUnreachableError` (3 sites, all registry lookups) | **DON'T count — DEMOTED** | No: re-executes an in-process dict built once at bootstrap. | HIGH |
| 2a | `LLMDispatchPayloadShapeError` — 3 pre-flight sites (`:323`,`:1266`,`:3507`) | **DON'T count — SPLIT OUT; requires the A-ii re-type** | No: re-validates the harness's own outgoing payload; same input, same verdict, every candidate. | HIGH |
| 2b | `LLMDispatchPayloadShapeError` — 25 response-parsing sites | **COUNT — unchanged** | Yes: re-parses a NEW provider response. | HIGH |
| 3 | `.status_code ∈ {401,403}` duck-type | **COUNT — strengthened** | Yes: only provider SDK exceptions carry `.status_code`; key rotation genuinely changes the answer. | HIGH |
| 4 | `MemoryToolExecutionInternalError` | **DON'T count** | No: harness wiring fault, candidate-independent. | HIGH |
| 5 | `MemoryToolExecutionInputError` | **DON'T count** | No, at type level: "caller- or model-supplied" + refusal against harness-held state. | HIGH |
| 6 | *prospective* B-115 (b′) conflict | **DON'T count — CONDITIONAL; does not close with B-116** | Unknown until B-115 builds; racy ⇒ VOID + C5 reroute. | MODERATE |

**Guard predicate, final:** charge only on a fault meeting the recovery-model test; realized as a negative check over the four-type harness-internal tuple at `:1028`, ≈30-35 src lines across two files, on `record_failure` only. **Reading (II) is undisturbed — F-01/F-02 push toward it, F-07 removes its strongest counter.**

## Registered forward rows (C9; none priced into B-116)

- **R1 — wire the dead half-open latch** (zero production call sites; §14.6's normative test now depends on it — priority RAISED by F-06).
- **R2 — FM-O: no per-provider breaker constructed** (enum member exists; only PER_MODEL built at `:662-665`).
- **R3 — FM-Q: `_emit_breaker_transition` (`:1130-1136`) passes no permanent_fail_repeats / tool_id / model_version.**
- **R4 — NEW (F-01): rename/re-type `LLMDispatchProviderUnreachableError`** — Class 2 back-flow (C-RT-14 token in two cleared specs); taxonomy value is C5/C7/OD's.
- **R5 — NEW (F-01): bootstrap-time validation that every chain candidate's provider is registered** (config faults fail at stage 3a, not at a runtime health counter); C1/C11 own the surface.
- **R6 — no replacement counter in this leg**, surviving only with the sampling-floor guarantee attached — now contingent on the t3 leg (see C7's E2b conversion).
