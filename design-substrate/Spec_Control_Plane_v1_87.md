# Spec: Control Plane — v1.87 (delta over v1.86)

*Delta-only file. The v1.86 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-3C-PREWARM bundled-absorption arc: materializing **ADR-D4 §1.8** (concurrent-prompt-cache warm-up protocol, steps 2-4) at the **WorkflowDriver PARALLELIZATION PROCEED** path. Net: two additive `bool = False` fields (one on `D4MultiplicativeTunable` §11.4, one on `WorkflowManifestEntry` §6.1 extension clause) + the `_same_prefix_cohort` predicate + `_proceed_fanout` two-phase (serialize-`branch[0]`, then `gather` rest) in `_execute_parallelization`. NO contract/enum/fail-class/§5.2-hash/CXA change; default-False → byte-identical to the all-concurrent baseline at default.*

## Change-note (v1.86 → v1.87)

**What this materializes.** ADR-D4 §1.8 commits: "on fan-out dispatch, dispatch `siblings[0]` synchronously (cache-write at breakpoint), then dispatch `siblings[1..N-1]` concurrently (cache-hit on shared prefix)." Prior to this delta, `_execute_parallelization` always ran all branches concurrently via `asyncio.gather`. This delta adds the **opt-in default-OFF** two-phase variant, gated by:

1. `_d4.concurrent_cache_warmup` (the new D4 tunable field, resolved from `manifest_entry.concurrent_cache_warmup`)
2. `_same_prefix_cohort()` predicate: all branches uniform in `(step_kind == INFERENCE_STEP, model_binding.provider, model_binding.model, agent_role, prompt_version_sha, extended_thinking)` **and** `len(branch_plan) >= 2`

**Scope of revision.**

**§11.4 — `D4MultiplicativeTunable` gains one additive field:**

> `concurrent_cache_warmup: bool = False` — opt-in gate for the PARALLELIZATION PROCEED warm-up (ADR-D4 §1.8). When `True` and `_same_prefix_cohort()` holds, the driver serializes `branch[0]` (cache-write) before releasing `branches[1..N-1]` (cache-hits). Default `False` → byte-identical to the all-concurrent baseline. Propagated by `d4_tunable(cell, persona_tier, *, concurrent_cache_warmup=False)` from the corresponding `WorkflowManifestEntry` field. PROCEED-only in this first slice; CASCADE_CANCEL/PAUSE are registered follow-on `B-18-3C-PREWARM-CASCADE`.

**§6.1 — `WorkflowManifestEntry` gains one additive optional field (§6.1 "additional per-workload fields" extension clause):**

> `concurrent_cache_warmup: bool = False` — operator-set per-workflow opt-in for the ADR-D4 §1.8 concurrent-prompt-cache warm-up protocol. Propagated by `d4_tunable(...)` alongside `cascade_policy` as `_d4.concurrent_cache_warmup`. Default `False`; construction-time omission preserved across every existing fixture (the `fanout_timeout_disposition` / `default_gate_level` / `entry_version` additive-optional precedent). Operator asserts: the deployment is Anthropic-routed, `frozen_tool_superset` is bound, no per-branch `memory_runtime` (CP-invisible — the operator-asserted residual scope per `.harness/u1-3c-prewarm-design-decision-record.md` §11.2).

**§25.15 (C-CP-25 — PARALLELIZATION PROCEED path) — the two-phase warm-up protocol:**

Under `CascadePolicy.PROCEED` (and only there), `_execute_parallelization` evaluates:

```
_warmup_gate: bool = _d4.concurrent_cache_warmup AND _same_prefix_cohort()
```

where `_same_prefix_cohort()` returns `True` iff:

- `len(branch_plan) >= 2` (H3 — degenerate resume guard: live plan length, NOT cell cap)
- All branches have `step.step_kind == StepKind.INFERENCE_STEP` (shared-dispatcher invariant per step_kind)
- All branches share `binding.model_binding.provider` and `.model` (Anthropic cache is per-model)
- All branches share `binding.agent_role` and `binding.prompt_version_sha` (system-prompt resolution)
- All branches share `extended_thinking` derived from `step.step_payload.get("params", {}).get("thinking")` (thinking forecloses the system marker per ADR-D3 §1.5)

Memory-packet fields (`memory_runtime`, `frozen_tool_superset`, cache-floor) are **NOT checked** by the predicate (CP-invisible — operator-asserted residual scope).

When `_warmup_gate` is `True`, `_proceed_fanout` runs in **two phases** (both bounded by the existing `asyncio.timeout(deadline)` wall-clock limit — H1 / M3 / M2 discipline):

```
phase 1: first = await _proceed_branch(*branch_plan[0])   # serialize: cache-write
         (Exception captured via try/except, NOT bare-await — H1: a branch[0] failure
          must still dispatch siblings and drain branch[0]'s buffered ledger entries)
phase 2: rest = await asyncio.gather(
             *(_proceed_branch(*p) for p in branch_plan[1:]),
             return_exceptions=True,                       # PROCEED: siblings not cancelled
         )
return [first, *rest]
```

When `_warmup_gate` is `False` (default — when `concurrent_cache_warmup=False`, or predicate fails, or cascade policy ≠ PROCEED), `_proceed_fanout` is **byte-identical to the pre-v1.87 all-concurrent baseline**: `asyncio.gather(*(...), return_exceptions=True)`. No behaviour change at default.

**Carrier discipline.** `concurrent_cache_warmup` is a **value-level gate** on a committed (but unbuilt) ADR-D4 §1.8 mechanism. It is NOT a new contract, NOT a new §5.2 hash dimension, NOT a new fail-class, NOT a new CXA edge. The D4 tunable already delivers `cascade_policy` to `_execute_parallelization` via the same channel; `concurrent_cache_warmup` rides that channel additive-alongside. The `WorkflowManifestEntry` field follows the `fanout_timeout_disposition` / `default_gate_level` / `entry_version` §6.1 extension-clause precedent.

**Fable-5 decorrelated review.** Full-transcript adversarial review (Agent model:"fable", 2026-07-10) pre-build, per `[[fable5-fallback-reviewer]]`. Outcome: SOUND-WITH-AMENDMENTS. Three must-fix findings (H1 exception-capture; H2 predicate strengthening + memory-runtime exclusion; H3 length-gate) plus M1–M8 test-plan gaps — all incorporated before any code was written. Post-build: out-of-family Codex pre-PR review (§13.1 standing discipline). Both reviewers cleared.

**Invariants preserved.** NO §5.2 IS-hash change. NO new contract / ADR / enum / fail-class / CXA edge / `StepDispatcher` Protocol widening. NO contract removal. The `D4MultiplicativeTunable` and `WorkflowManifestEntry` additions are additive-optional (default `False`). All existing PARALLELIZATION tests (including PAUSE/CASCADE_CANCEL paths) pass byte-identical; the warm-up two-phase path is tested by `test_workflow_driver_parallelization_warmup.py` (6 tests, all green).

**Registered follow-ons (SPINE `B-*`).**

| Follow-on | Scope |
|---|---|
| `B-18-3C-PREWARM-COHORTKEY` | `StepDispatcher.cohort_key() -> str | None` Protocol method — dispatcher-attested cacheability; `None` = unstable prefix (memory_runtime / no superset / sub-floor). Replaces the operator-asserted residual scope with a machine-checkable signal |
| `B-18-3C-PREWARM-CASCADE` | warm-up on CASCADE_CANCEL + PAUSE paths (TaskGroup + snapshot surface) |
| `B-18-3C-PREWARM-DEFAULT-ON` | flip to required-at-cap>1 per ADR §1.8(f) once the mechanism is proven + `B-18-3C-PREWARM-COHORTKEY` lands |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition (warm one per cohort) |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_87.md` (delta over v1.86) |
| Arc | B-18-3C-PREWARM — concurrent-prompt-cache warm-up (ADR-D4 §1.8) |
| Committed source | ADR-D4 v1.1 §1.8 (materializing steps 2-4; step 1 = C2-owned plan-persist, NOT this arc) |
| Disposition | Additive `bool=False` fields on `D4MultiplicativeTunable` (§11.4) + `WorkflowManifestEntry` (§6.1); two-phase `_proceed_fanout` on `_warmup_gate` (PROCEED only, opt-in); byte-identical at default |
| Decorrelated review | Fable-5 pre-build adversarial review (H1/H2/H3 amendments; 2026-07-10) + out-of-family Codex pre-PR (§13.1) |
| IS / OD / AS / ADR | UNCHANGED. ADR-D4 §1.8 is the committed source (impl-of-committed, not extension). CXA v2.20 UNCHANGED |
| Runtime spec | UNCHANGED (the harness-runtime manifest-loader's `_WorkflowSection` carrier gains `concurrent_cache_warmup` by the §14.19.4 byte-exact-projection invariant — impl-to-cleared-spec on the existing extension-clause precedent, NO runtime spec delta owed) |
| Follow-on registrations | `B-18-3C-PREWARM-COHORTKEY` · `B-18-3C-PREWARM-CASCADE` · `B-18-3C-PREWARM-DEFAULT-ON` · `B-18-EPOCH-PARTITION` |
