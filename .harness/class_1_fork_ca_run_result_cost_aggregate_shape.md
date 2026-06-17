# Class 1 Fork — CA run-result cost-aggregate shape (C-RT-09 `cost_attribution` axis + type-name reconcile)

**Filed:** 2026-06-17 · R-FS-1 arc **CA** (cost aggregate — `RunResult.cost_attribution` rollup), bundled-absorption posture (runtime spec v1.52 → **v1.53** §9 C-RT-09 amendment + `harness-runtime/src`). Class 1 (X-AL-3 spec **contract extension** on a cleared spec — the run-result aggregate SHAPE was under-specified). Design back-flow FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + design decided (axis + type-name + invocation contract) — drives the impl. **NO operator gate** — unlike B4 Slice 4 (which relaxed a committed §14.5.3 invariant), this fork is **additive/clarifying and sacrifices no committed invariant**; it names the axis the cleared field already typed and reconciles a phantom type-name. Adopt-and-note per workspace `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`; advisor-confirmed (advisor-not-council, no AUQ).

## §1 The fork

C-RT-09 §9 names the field `cost_attribution: CostAttribution (OD type)` = *"Aggregated 5-step cost-attribution rollup"* — **one line**. It is under-specified in three ways, and the field has been hard-coded `cost_attribution=()` at `_build_run_result` (`api.py:962`) since landing — gated behind the (now CLOSED) `U-OD-21` HALTED Class-1 tension. Arc CA wires it.

1. **No `RollupAxis` named.** The OD aggregate primitive `rollup_costs_by_axis(records, axis)` (`harness_od.cross_family_rollup:171`) takes **one** of three axes (`PER_PROVIDER_DISCRIMINATOR` / `PER_PROVIDER_AND_MODEL` / `PER_FALLBACK_EVENT`); the spec sentence states none.
2. **`CostAttribution` is a phantom type.** OD exports no type literally named `CostAttribution` (grep-confirmed at HEAD). The code field type is `tuple[CrossFamilyCostRollup, ...]` (`api.py:332`); the drift is already logged Class-3 at `api.py:335` + the module docstring.
3. **No statement** of whether per-run aggregation is a **new** contract vs the C-OD-15 §15.1 dashboard rollup.

## §2 Resolution

### §2.1 Axis = `PER_PROVIDER_AND_MODEL` (empirically forced; the sweep's lead is wrong)

The arc-CA grounding sweep led `PER_PROVIDER_DISCRIMINATOR` ("most operator-meaningful"). **HEAD body-grounding overturns it — that axis is INADMISSIBLE under current dispatch-type tagging:**

- `rollup_costs_by_axis(PER_PROVIDER_DISCRIMINATOR)` **validates** `SpanCostRecord.provider_discriminator` against the bounded `CrossFamilyTag` vocabulary and **raises `CrossFamilyRollupError`** on a non-member (`cross_family_rollup.py:192-193, 156-168`).
- `CrossFamilyTag = {frontier_managed, frontier_managed_alt, local_ollama}` (`cross_family_rollup.py:64-76`) — a **fallback-provider-family** taxonomy.
- But every production cost helper writes a **dispatch-type** tag into `provider_discriminator`: LLM → `"llm"`, tool → `"tool"`, validator → `"validator"`, webhook → `"webhook"` (`cost_attribution_{llm,tool,validator,webhook}_dispatch.py` `_*_FAMILY_TAG`). **None are `CrossFamilyTag` members.**
- ⟹ `PER_PROVIDER_DISCRIMINATOR` would raise on **every** production cost record. (It passes in OD unit tests only because those construct synthetic `frontier_managed`/`local_ollama` records.)

`PER_PROVIDER_AND_MODEL` keys on `(gen_ai_provider_name, gen_ai_request_model)` with **no validation** (`cross_family_rollup.py:194-195`) — safe for all four dispatch types and operator-meaningful: LLM → `anthropic::claude-opus-4`; tool → `tool:<id>::`; validator → `validator:<id>::`; webhook → `webhook:<target>::`. `PER_FALLBACK_EVENT` is also safe but not chosen.

**Single axis, NOT all-three concatenated.** The field is a **flat** `tuple[CrossFamilyCostRollup, ...]`. Each entry carries its own `rollup_axis` (`cross_family_rollup.py:101`), so a multi-axis tuple is technically self-describing — **but** a naive `sum(e.total_cost for e in run_result.cost_attribution)` would **double-count** dollars (each dollar appears once per axis). A single axis preserves the natural **sum-invariant**: `sum(total_cost)` = true run cost. (advisor-confirmed.) → **`PER_PROVIDER_AND_MODEL`, single axis.**

### §2.2 Type-name reconcile: `CostAttribution (OD type)` → `tuple[CrossFamilyCostRollup, ...]`

Not a major-bump "rename" under the §9 version-evolution invariant: `CostAttribution` is a **phantom** (no real OD type ever existed; `api.py:335` + the module docstring already document this); the **code** field type has always been `tuple[CrossFamilyCostRollup, ...]` since landing. This is a spec-prose reconciliation to the actual materialized type. The behavioral change (`()` → populated) is **pure enrichment** — the declared code type is unchanged, no consumer that binds `tuple[CrossFamilyCostRollup, ...]` breaks. **Minor/clarifying bump (v1.53).**

### §2.3 Per-run aggregation = a new INVOCATION of the existing primitive, not a new contract

`_build_run_result` invokes the **existing** `rollup_costs_by_axis` (C-OD-15 §15.1) over the run-scoped accumulated records. Same primitive; what is new is the run-scoped record **source** (the in-memory accumulator, §4) + the run-result **invocation site**. The C-OD-15 §15.1 *dashboard* rollup remains a separate (impl-discretion / deferred) surface — no double authoring.

## §3 Latent Class-1 — the dispatch-type-vs-fallback-family taxonomy mismatch (registered as a BUILD arc)

The production helpers writing non-`CrossFamilyTag` `provider_discriminator` values into a field whose **contract** (`rollup_costs_by_axis` PER_PROVIDER_DISCRIMINATOR + the `SpanCostRecord.provider_discriminator` docstring "validated against `CrossFamilyTag`") validates against `CrossFamilyTag` is a **latent Class-1 contract-vs-production coherence defect** — dormant **only** because nothing currently runs PER_PROVIDER_DISCRIMINATOR on production records (the arc-CA sweep nearly tripped it). The dispatch-type breakdown (llm vs tool vs validator vs webhook cost) is arguably the **most** operator-meaningful rollup, and it is exactly the one this bug blocks. Under FULL-SPEC this is **registered as a real build arc** (NOT folded into a Class-3 throwaway): **`B-COST-DISCRIMINATOR-TAXONOMY`** in `.harness/beyond-mvp-capability-boundary-ledger.md` — reconcile the dispatch-type tag taxonomy against the `CrossFamilyTag` fallback-family taxonomy so PER_PROVIDER_DISCRIMINATOR (or a dedicated dispatch-type axis) becomes admissible on production records. **Out of CA scope** — PER_PROVIDER_AND_MODEL yields a correct run-result rollup without it.

## §4 Impl shape (impl-discretion)

- **Run-scoped accumulator = a `CostRecordAccumulator` HOLDER (NOT a bare `list`)** — a **Stage-0 PREAMBLE** field on `HarnessContext` (`cost_record_accumulator: CostRecordAccumulator`, default-factory holder; mirroring `drained_flag`/`tracer_provider` — created at the `_MutableHarnessContext` builder, threaded onto the frozen ctx at `freeze()`). **Why a holder, not a `list`** (advisor-caught + probe-confirmed): `HarnessContext` is a frozen **Pydantic** model, and Pydantic v2 **COPIES** a typed `list[SpanCostRecord]` field during construction validation at `freeze()` (`M(xs=lst).xs is not lst`) — the frozen ctx would then hold a *different* list than the one the stage-4/5 dispatchers captured pre-freeze, so dispatch appends would be invisible to `_build_run_result` → `cost_attribution` always `()` in production (a defect invisible to every test that doesn't traverse `freeze()`). The `drained_flag` precedent works *only because `asyncio.Event` is an arbitrary type* stored by reference; a known container is validated/copied. The `CostRecordAccumulator` (a plain, non-Pydantic class, `arbitrary_types_allowed`) is likewise stored **by reference**, so the holder — and its `.records` list — survive `freeze()` as the same object.
- **Threaded same-reference** into the four dispatcher/hook materializations (stage 4 validator hook; stage 5 LLM/tool/webhook) as `ctx.cost_record_accumulator.records` (the stable inner list — the holder is by-reference so `.records` is stable across freeze). Each best-effort wrapper appends its **already-returned** `SpanCostRecord` (all four helpers are `-> SpanCostRecord`). The wrappers stay `list`-based; only the ctx carrier is the holder.
- **`_build_run_result`** reads `ctx.cost_record_accumulator.records`, sets `cost_attribution = tuple(rollup_costs_by_axis(records, RollupAxis.PER_PROVIDER_AND_MODEL))`; empty records → `()` (preserves the trivial-workflow shape). Refresh the stale `api.py:911-914` docstring (the U-OD-21-HALTED carry is provably false at HEAD).
- **NOT audit-ledger read-back.** `CostRecordAuditPayload` (`cost_namespace.py:96-133`) drops the **required** `provider_discriminator` field (among others), so the persisted payload cannot reconstruct a full frozen `SpanCostRecord` for `rollup_costs_by_axis`. (The SSOT-purist read-back path = payload-widening + read-back, which touches the CXA `cost:`-prefix audit-write seam — correctly out of scope; the forward path if SSOT is later wanted.)
- **No thread-lock.** `list.append` is atomic under the GIL; the only read is **post-join** (after the `asyncio.to_thread` driver returns). Correctness requirement: the dispatchers and ctx hold the **same** `.records` list (the holder guarantees it across freeze).
- **No C-IS-05 §5.2 hash change.** The accumulator is ephemeral run-**output**, not a dispatch-determinism config dimension (contrast B4 Slice 1's per-role prompt selection, which DID affect injected content → needed hash widening). It records costs; it does not change what is dispatched.
- **Regression test (the bug-class guard):** `test_bootstrap_cost_accumulator_survives_freeze_by_reference` bootstraps a real frozen ctx and asserts the bare tool dispatcher's sink **IS** `ctx.cost_record_accumulator.records` — the exact seam the Pydantic-copy would sever, and the one every other CA test (which passes lists/sinks directly, bypassing `freeze()`) cannot catch.

## §5 Decorrelated review

- **advisor** (pre-build, full transcript): confirmed the forced axis + the single-axis sum-invariant + the in-memory accumulator; flagged (1) verify the 4-dispatcher wiring actually composes before claiming "wire all 4" — **verified composes** (each has a stage-bound best-effort wrapper reaching a shared sink); (2) register the taxonomy mismatch as a real build arc, not a Class-3 throwaway — **done (§3, `B-COST-DISCRIMINATOR-TAXONOMY`)**; (3) sharpen the read-back rationale (dropped **required** field, not vague "lossy") — **done (§4)**.
- **advisor** (pre-done, full transcript): caught a **production-dead bug** the green suite structurally could not — the same-reference invariant was broken at `freeze()` because Pydantic v2 copies a typed `list[...]` field (the first impl used a bare `list`). Probe-confirmed (`M(xs=lst).xs is not lst`); fixed by the `CostRecordAccumulator` arbitrary-type holder (by-reference, like `drained_flag`/`tracer_provider`) + the `freeze()`-traversing regression test (§4). This is the §13.1 "green-unit-tested but unreachable through bootstrap" failure mode — caught before merge.
- **Codex** (`just codex-review`) — pre-merge, out-of-family (clean on the pre-fix diff; the holder fix is re-reviewed pre-merge).
- **Council** not warranted: the `CrossFamilyTag` foreclosure **probe-resolves** the axis choice (no nameable cross-domain tension survives) per `[[probe-resolves-fork-prescribed-council]]`; the grounding sweep itself said "council not warranted."

## §6 Build slices

- **Slice 0** (this fork + spec v1.53 §9 amendment + clearance marker + `B-COST-DISCRIMINATOR-TAXONOMY` spine registration).
- **Slice 1** — `cost_record_accumulator` Stage-0 field (types.py + mutable_context.py + stage_0_preamble.py).
- **Slice 2** — thread the sink into the 4 materializations + append in the 4 best-effort wrappers.
- **Slice 3** — `_build_run_result` rollup + docstring refresh.
- **Slice 4** — e2e (non-empty `cost_attribution` with correct per-(provider,model) sums) + `_build_run_result` unit + field-assert test updates.

Slice 5 (fan-out parent/child double-counting, 14.3 vs 15.1) is **NOT in scope** and **not owed** for the run-result PER_PROVIDER_AND_MODEL aggregate: each real dispatch contributes exactly one record once → no parent/child double-counting at the per-dispatch level. The 14.3 `rollup_fanout_at_close` is a distinct dashboard surface, not this run-result field.
