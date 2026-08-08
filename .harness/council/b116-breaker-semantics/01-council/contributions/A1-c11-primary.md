# A1 — C11 (Operator Loop & Local-First) primary contribution — B-116 (verbatim, 2026-08-07)

# C11 — Operator Loop & Local-First Deployment · B-116 contribution

**Co-primary scan.** This topic engages **C9** (breaker mechanism / threshold discipline) and **C1** (candidate-advance placement). I am NOT authoring the trip threshold, the fail-class taxonomy, or the classifier's control-flow contract — those are C9's and C5's. I speak to what the **operator sees**, what **survives restart**, and whether the resulting state is one a solo operator on their own machine can get out of. Per the fork's own framing this is a declared dyad, so I proceed as one half, not as a single-voice answer.

## Position: **(II), with the §5 per-member split — plus a mandatory non-counted-fault visibility term I require before the build leg lands**

**First cite.** C-CP-03 §3.4 (`design-substrate/Spec_Control_Plane_v1_2.md:391`, re-tabled at `Spec_Control_Plane_v1_3.md:75`; §3.4/§3.5 are last substantively defined at the v1.2 baseline of the CP delta chain whose head is v1.115, so this resolves byte-exact per the workspace delta-baseline convention): *"circuit breakers attach per-`{provider, model}` pair."* The mechanism is **keyed to a provider fact**. A fault that is candidate-independent by construction has no true value on that key — it is not a fact *about* `anthropic:claude-3-5-sonnet`. Charging it there is a type error dressed as a counter. [HIGH]

**The finding that decided me is not the one in the filing.** I read the fail-fast path end to end and the "counting is at least loud" premise behind reading (I) is **empirically false at HEAD**:

1. **Before** the breakers open, the operator's terminal is *correct and loud*: `_failure_detail` (`retry_breaker_fallback.py:178-187`) composes `MemoryToolExecutionInternalError: <message>`, `RetryBreakerFallbackExhaustedError.__init__` (`:169-175`) appends it as `; last failure: …`, `_step_fail_class` (`harness-cp/src/harness_cp/workflow_driver.py:1686-1687`) interpolates `str(exc)`, and the CLI echoes it to stderr (`harness-runtime/src/harness_runtime/cli/app.py:141-143`, `:243-244`). Push-mode, right reason, every dispatch. [HIGH]
2. **After** the breakers open, that signal is **destroyed**. The breaker-open pre-check sets `last_failure_detail = None` (`retry_breaker_fallback.py:683`) and `last_failure_class = "breaker-open"`. The operator's terminal line collapses to a bare chain-exhausted message with **no cause at all**, and the only telemetry is `retry.skipped.reason = "breaker-open"` — a claim about provider health that is false. [HIGH]

So counting does not make the misconfiguration louder. It makes it **quieter and mislabeled**, and it does so on exactly the `fail_threshold`-th dispatch — i.e. after the operator has retried enough times to be frustrated. Reading (I)'s cost is not "misleading telemetry"; it is **loss of the one correct operator-facing signal the system already emits**. That inverts the question the prompt poses to me: it is not "loud-but-wrong vs. right-but-unread." It is **right-and-pushed vs. wrong-and-pushed-after-erasing-the-right-one**. [HIGH]

**Two local-deployment facts that harden this** (my §4.1.27 / persistence-posture obligations):

- **No operator-facing breaker readout exists.** A whole-directory search of `harness-runtime/src/harness_runtime/cli/` for `breaker` returns **zero** hits. Breaker state reaches the operator only as span events in the trace store — read through the terminal TUI browser, which is architecture-committed but phase-2. Asserting "telemetry surfaces it" without naming a live surface is FM-J; I will not do it in either direction. [HIGH]
- **Breaker state is in-memory at HEAD** — no `breaker_state` table is wired anywhere in `harness-runtime/src` or `harness-od/src`; the durable posture at §4.1.27 is designed, not built. Today the blast radius of Probe C is bounded to the process lifetime. **The moment `breaker_persistence=durable` lands, a config typo becomes a cross-session outage that survives the restart the operator will reach for.** Deciding (II) *now*, before durability, is materially cheaper than deciding it after. [HIGH]

Under reading (I) the solo operator's move set is: restart (breakers reset, misconfiguration persists, all breakers re-open within `fail_threshold` dispatches) or wait out cooldown (half-open → one deterministic failure → open again, `retry_breaker.py:239-251`). Neither terminates. That is an unrecoverable state reachable from a single unset config field. [HIGH]

## Per-member dispositions

| # | Member | C11 disposition | One-sentence reason |
|---|---|---|---|
| 1 | `LLMDispatchProviderUnreachableError` | **count** | A genuine provider fact keyed to the right `{provider, model}`; the open breaker is a true statement and the operator's remedy (wait / switch provider) matches it. |
| 2 | `LLMDispatchPayloadShapeError` | **count** | Provider-boundary fact; keeping it counting preserves the breaker's protection of the exact surface it was built for. |
| 3 | `.status_code ∈ {401, 403}` duck-type | **count** | Provider-attested credential fact — and the operator's remedy is a *named local-deployment command* (`harness secrets rotate <name>`, §4.1.14) against the keychain hierarchy (§4.1.13), so an open breaker on a real auth failure points at the right fix; `_classify_breaker_cause` (`:409`) already tags it `AUTH_FAILURE`, so the telemetry names the reason correctly. [MODERATE] — this is the one counting member that is also frequently an *operator* fault, and I accept it only because the provider asserted it. |
| 4 | `MemoryToolExecutionInternalError` | **don't count** | Harness-internal by construction and candidate-independent — Probe B shows one dispatch burning budget on every breaker across both providers; it is not a fact about any `{provider, model}`. |
| 5 | `MemoryToolExecutionInputError` | **don't count** | Same nature; the C-MEM-19 v1.3 re-typing hardened this boundary precisely so the harness-internal set stays nameable, and C-MEM-19 explicitly disclaims owning breaker classification. |
| (6) | *prospective* B-115 (b′) ledger-idempotency conflict | **don't count — decide it here** | Same construction; deciding it now costs one table row, deciding it after the B-115 build leg costs a second fork and a second witness re-pin. |

## Strongest argument against my position, stated fairly

Reading (II) makes the breaker's protection contingent on a **hand-maintained type allowlist** — and this fork exists precisely because that set grew five times (B-41 / B-84 / B-88 / B-114, prospectively B-115) with **no §14.6 amendment each time**. If a genuinely provider-attributable fault is ever mis-typed into the harness-internal column, the breaker silently stops protecting a real failing chain — and that failure is **invisible**: no state transition, no `breaker.tripped` event, nothing on the terminal. Over-counting announces itself (breakers open, loudly wrong). Under-counting does not announce itself at all. For a solo operator with no on-call rotation and no dashboard, a **silent** loss of protection is a defensible thing to fear more than a **loud** wrong one, and my §4.1.24 trace-browser default does not yet exist to catch it. [HIGH]

My answer, honestly bounded: (i) the fail-fast set is *already* hand-maintained for control flow, so (II) adds a second column to an existing table rather than a new maintenance axis; (ii) requirement (c) below converts the non-counting decision from silent to inspectable; (iii) the members at issue are `MemoryTool*` types raised by harness code, not wrapped provider exceptions. But the cost is real and should be recorded on the row, not argued away.

## Refinements my domain requires of the §6 priced fix

**(a) The non-counted fault MUST stay on the operator's terminal, verbatim.** The ~12-line guard must touch `record_failure` **only** — `last_failure_detail` (`:1031-1035`) and the `fallback.exhausted` event's `fallback.last_failure_class` must keep carrying `type(exc).__name__` and the bounded message. A non-counted fault that becomes `"unknown"` is strictly worse than counting it. Add this as an explicit assertion in the Probe-B/C witnesses, not just `fail_count == 0`.

**(b) `retry.breaker_charged` (bool) on the inner attempt span — declared, not slipped in.** Without it, no future reader can distinguish *"the harness deliberately did not charge this"* from *"the harness forgot."* This is an **accretion-pattern addition to C7's catalog** under my local-trace-UX co-primary (the §4.1.10 precedent); **C7 owns the attribute name and semconv placement** — I own only the requirement that the local trace browser can filter on it. Route it, do not author it here.

**(c) Registered adjacency, NOT in this scope: the `last_failure_detail = None` at `:683`.** Members #1–#3 keep counting, so the breaker-open detail-erasure keeps producing "everything is broken, no reason given" for genuine provider outages. That is a separate operator-experience defect with its own cause; I flag it for a row rather than widen this diff (surgical-change discipline).

**(d) No HITL here. Explicitly.** A deterministic config fault that already fails the step with a typed, terminal-visible error is not a blast-radius outlier and does not warrant a gate — gating it is FM-F (gate-fatigue), and the correct C11 answer is **no HITL surface at all**. No operator-prose palette is introduced, so there is nothing to map back to {approve / edit / reject / respond} (FM-G satisfied vacuously). The surface is the typed error plus the stderr line, and that is sufficient. [HIGH]

**(e) Persistence posture, stated so it cannot drift (FM-I).** The guard introduces **no persisted state**; breaker state stays **in-memory, fresh-on-restart** at HEAD, consistent with my §4.1.27 default. If `breaker_persistence=durable` is later wired to the sqlite `breaker_state` table, the guard **must** hold on that path too — a durable breaker opened by a harness-internal fault would survive the restart the operator reaches for first. Pin this as a sentence in the §14.6 step-4 amendment, not only in code.

**Standing cross-cutting pre-checks.** **#1 blast radius (C10):** none — the guard removes a state transition, adds no capability, crosses no trust boundary. **#2 observability (C7):** one proposed attribute per (b), plus the preserved `fallback.last_failure_class`; C7 adjudicates the name. **#4 reliability (C9):** the recovery path for the non-counted class is unchanged — fail-fast, advance, exhaust, typed terminal error; what changes is only whether a candidate-independent fault is charged to a provider-keyed counter, which is C9's mechanism but my operator-recoverability concern.
