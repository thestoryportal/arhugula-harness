# HarnessContext carrier + hash-coherence patterns

*Runtime-implementation pattern note (NOT `design-substrate/**`; NOT a Project_Workflow §7.5 process discipline — see `R-600-pattern-bake-in-sweep.md` cadence-5 §2 disposition). Consolidates six recurring gotchas around adding a new `HarnessContext` field or a new hash-fed carrier, empirically caught across six independent R-FS-1 arcs by `advisor()` pre-done review + out-of-family Codex. Source: memory `[[new-surface-audit-hash-and-config-not-carrier]]` (2026-06 through 2026-07). Filed 2026-07-12 at the R-600 cadence-5 sweep as the recommended dedicated home for a pattern that clears §7.5.1 gate 1 (6 independent arcs) but fails the domain-fit implicit in §7.5.4 — this checklist is subsystem-specific implementation mechanics, not a cross-project SDLC discipline.*

---

## When this applies

Any arc that adds a **new behavior-driving or injected surface** to the runtime (a per-role prompt, a cost value, a sandbox tier, an operator-config flag) — or that adds a **new field to `HarnessContext`** or to any carrier whose `model_dump()` feeds a hash. Run the checklist below before merge; each item was caught by `advisor()` or Codex missing it on a first draft, not by a rule stated anywhere else in the codebase at the time.

## 1. Audit-hash coherence

The C-IS-05 §5.2 procedural-tier snapshot is the run-level fingerprint; §14.5.2 forbids it reporting "unchanged" while injected content changes. When a new surface makes something behavior-driving reach the outside world, check whether the hash actually captures the new dimension. **Fast tell:** does a sibling surface already get hashed? If a parallel dimension IS captured and yours ISN'T, that's the gap (B4 #616 — `routing_manifest` was hashed, the per-role prompt-selection manifest wasn't). Fix by widening the recipe (e.g. add a whole-manifest SHA mirroring the sibling), which is a forward-only hash rebase C-IS-05 §5.2 already anticipates.

## 2. Read `ctx.config.X`, don't mint a carrier, for a pass-through value

`HarnessContext` fields are enumerated by runtime spec §4 C-RT-04 with a parity test (`test_harness_context_declares_all_c_rt_04_fields`). Adding a field requires a spec amendment. **Discriminator:** is the value stage-enriched/reconciled (earns a dedicated ctx carrier + a C-RT-04 row), or is it a config pass-through (`ctx.X == config.X`, zero enrichment — read `ctx.config.X` directly, no carrier, no spec row)? B4 #616 drafted an unnecessary carrier for a pure pass-through; dropping it was strictly less code and zero spec debt. A builder-transient value resolved at bootstrap and consumed by a later stage lives on the mutable bootstrap ctx only, never the frozen model.

## 3. The `freeze()` path — three independent failure modes for a new carrier field

If a slice genuinely earns a `HarnessContext` carrier (per §2), `_MutableHarnessContext.freeze()` has three distinct bite-modes, all observed across R-FS-1 arcs:

- **(a) freeze-by-ref.** Pydantic v2 copies a typed `list[...]`/`dict[...]` field at construction, severing any run-scoped mutable state captured before freeze. Fix: a plain (non-Pydantic) arbitrary-type holder stored by reference under `arbitrary_types_allowed`, so the same object survives freeze. Add a `test_*_survives_freeze_by_reference` that asserts identity, not just value equality — a value-equality test cannot see this bug (CA #625).
- **(b) freeze-constructor omission.** `freeze()` is a hand-written ~30-line constructor, not derived from `__dict__` — a field set on the mutable builder silently defaults (usually `None`) on the frozen object unless you also add the explicit `field=self.field` line. Pyright is silent (the default is type-valid) (M #635).
- **(c) no-reader discriminator.** Before writing a heavy positive freeze-passthrough test, grep for a post-freeze reader of the field. A write-only forward-capability carrier (nothing reads `ctx.X` after freeze yet) only needs structural coverage — the field exists in `model_fields` + the `field=self.field` line is present in `freeze()`. Reserve full behavioral tests for fields with a real behavioral reader.

## 4. Daemon-reuse lifecycle for a by-ref holder

A (3a) by-ref holder is allocated once at bootstrap, but its content is per-run. In daemon-client mode (U-RT-108) one bootstrapped context serves many `run_workflow` invocations, so a holder accumulating run-scoped state leaks across runs unless:

- **(a) Sequential reuse** — `reset()` the holder at each non-resume run boundary (mirrors the existing discipline for `workflow_registry`/`_harness_ctx`).
- **(b) Concurrent reuse** — a per-running-loop `asyncio.Lock` (keyed by loop, not a single module-level lock) around `[reset + execute]`, acquired only when the feature is bound, so opt-out keeps full concurrency.
- **(c) Timeout-zombie residual.** On a `drain_timeout_seconds` timeout the awaiting task is cancelled but the non-cancellable worker keeps writing — no lock can fence it. This is systemic across every bootstrap-ctx holder, not fixable per-holder; the real fix is per-run isolation (a `ContextVar`-scoped holder). Register it as one cross-cutting arc rather than patching each holder; bound the invariant honestly to what was actually closed (B-INTERSTEP #651 took 3 Codex rounds to fully surface all three sub-cases).

## 5. Carrier choice has hash consequences — pick the hash-inert carrier for a non-hashed field

A new per-step field that is NOT meant to be hashed must avoid a carrier that already feeds a hash. In this codebase, `StepEffectiveBinding.model_dump()` feeds the C-CP-06 §16.5.4 per-step override outcome-hash; the procedural-tier snapshot feeds §5.2; `StepExecutionContext` is hash-inert (not `model_dump`'d into any ledger entry). Before adding a field, grep whether the candidate carrier's `model_dump` reaches a hash-compose function; a field meant to drive behavior without shifting identity goes on the inert carrier (B-HITL-PLACEMENT-PER-STEP-PRODUCER #657).

## 6. A default-None field on a hash-fed carrier needs drop-when-None, path-aware if the carrier nests

Adding an additive `field: T | None = None` to a carrier whose `model_dump` feeds a hash shifts every pre-existing snapshot's hash unless the key is dropped from the canonical serialization when `None` (`model_dump` always emits the key, even as `null`). Three sub-modes, each a real correctness catch over 4 Codex rounds on B-FANOUT-PAUSE-SYNTHESIS #728:

- **(a)** a top-level-only drop misses a carrier nested inside another carrier's `model_dump` (e.g. a hierarchical parent snapshot embedding a child snapshot with its own instance of the same field) — recurse to the nested carrier paths.
- **(b)** a blanket recursive walk over-reaches into user/LLM-authored payloads, silently stripping a same-named user key — the drop must be **path-aware**: only the carrier's own known field, only along known nested-carrier paths, never through recovered-output payloads. Witness it with a test where a recovered output literally named the same key stays hash-covered.
- **(c)** at resume, read the *resuming strategy's* expected carrier, not "whichever populated carrier is present" — a carrier/topology mismatch can otherwise silently re-run the whole operation from scratch (an at-most-once violation) instead of failing closed on the mismatch.

## Cross-references

memory `[[new-surface-audit-hash-and-config-not-carrier]]` (source); `[[shared-is-shape-change-ripples-cross-axis-field-asserts]]` (the field-set parity test ripple every new carrier field owes); `[[full-chain-witness-not-half-proofs]]` / Project_Workflow PD-6 (the composed-chain witness discipline these hazards are usually caught by); `[[verification-shape-sharpened-grep-vs-e2e]]` / PD-3 (structural vs. behavioral coverage per item 3c); `[[hooks-codex-pilots-decorrelation-validated]]` (several of these were Codex-only catches, advisor + author missed them).
