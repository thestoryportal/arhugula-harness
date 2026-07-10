# U-1 slice 3c — concurrent-prompt-cache warm-up: design decision record (pre-build)

*Authored 2026-07-10 (dedicated fresh session for the high-blast-radius pre-warm arc, per the `B-18-3C-PREWARM` handoff). Build DEFERRED to a next session with advisor available (operator decision, this session): this DDR captures the fully-grounded design so advisor + operator can vet the load-bearing calls before any edit lands in the fan-out core. Process-substrate (`.harness/`), NOT a design-substrate edit — no X-AL-3 concern. Confidence tags per §10.4.*

---

## 0. TL;DR

- **Scope this arc = `3c-homogeneous` only** (the findings-doc §Correction recommendation): the *binary same-prefix gate* + serialize-`branch[0]`, on the **PROCEED** cascade path only, **opt-in default-OFF**. This is the lowest-risk non-hollow slice. `[HIGH]`
- **The full `version_sha` cohort HASH (3b-epochkey) is NOT needed for the homogeneous slice** — a sound-conservative binary predicate (all siblings uniform in `(agent_role, prompt_version_sha)` + shared `frozen_tool_superset` by construction) answers "same cohort?" without computing the hash. The hash is only needed for the **deferred heterogeneous partition** (3c-full), where you group N siblings into K cohorts and warm one per cohort. `[HIGH]`
- **Gate carrier = a new field on the D4 multiplicative tunable** (`concurrent_cache_warmup: bool = False`), resolved per-cell via the existing `d4_tunable(...)` alongside `cascade_policy`. ADR-D4 §1.8 frames warm-up as a per-cell property ("applies to all cells where fan-out cap > 1"), so this is the architecturally-coherent home. `[MODERATE]`
- **Integration = reuse `_proceed_branch` for the serialized `branch[0]`, then `gather` the rest** — this preserves EVERY fan-out invariant (per-branch ledger entries, the RESERVE-before-COMMIT replay-store `record_branch`, effect-fence, drain, `collected`, `terminal_dispositions`) with ZERO new bookkeeping, and makes crash-resume-mid-warm naturally correct. `[HIGH]`
- **ADR-vs-guardrail tension resolved: opt-in default-OFF for this first slice** (findings §Correction guardrail), even though ADR-D4 §1.8(f) says warm-up is *required* at cap > 1. The opt-in is an implementation-safety staging choice; flipping the default to the ADR's required-at-cap>1 is a registered follow-on once the mechanism is proven. `[HIGH]`
- **CP-spec touch** (bundled absorption): D4-tunable field + §25.15/§1.8 materialization + clearance marker. NO IS/runtime cohort-hash needed for this slice. `[MODERATE]`

---

## 1. What the ADR commits (the cleared design being materialized)

**ADR-D4 §1.8 (lines 228-240)** — Concurrent-prompt-cache warm-up protocol:

```
on_fanout_dispatch(siblings, cache_breakpoint_id):
    1. lead_agent.persist_plan_to_filesystem(plan)   # C2-owned; orthogonal (NOT this arc)
    2. dispatch siblings[0] synchronously            # cache-write at breakpoint
    3. await siblings[0].cache_acknowledgement OR
       await siblings[0].first_token_emission        # cache write completion proxy
    4. dispatch siblings[1..N-1] concurrently        # cache-hit on shared prefix
```

- §1.8(f): *"Concurrent-prompt-cache warm-up protocol is **required** at fan-out cap > 1... cost-amortization (cache-hit on remaining N-1 siblings) outweighs [the one-sibling-latency] at any fan-out cap ≥ 2."* `[HIGH]`
- Step 1 (plan persistence) is **C2-owned, orthogonal** — NOT part of this arc (harness-owned steps 2-4 only). `[HIGH]`
- **Guardrail deviation from step 3** (findings §Correction, advisor-directed): Anthropic gives **no cache-acknowledgement signal and no usable first-token hook** at the harness layer. The write is known-landed only after `branch[0]`'s *response* carries `cache_creation_input_tokens > 0`. So step 3 becomes **"await `branch[0]` to full completion"** — a stronger (safe) proxy than first-token. `[HIGH]`

---

## 2. Cohort identity — why the homogeneous slice needs only a binary predicate

The cacheable Anthropic prefix is **`[frozen_tool_superset + system_prompt]`** (the slice-1/2/3a breakpoint). Two siblings share a warm cache **iff** this prefix is byte-identical (Anthropic cache is byte-exact — ADR-D3 §1.5 line 204; ADR-F2 §(b)(ii)). The two components: `[HIGH]`

| Prefix component | Per-branch variability | Source |
|---|---|---|
| `frozen_tool_superset` | **SHARED across all siblings** (bootstrap-bound on the one dispatcher; child-superset uniform per slice 3a) | `llm_dispatch.py:579` field; `dispatch()` selects parent vs `child_frozen_tool_superset` at 1320-1337 |
| `system_prompt` | **the SOLE per-branch variable** | resolved at `llm_dispatch.py:1005-1037`: `binding.prompt_version_sha` (per-step override) → `per_role_system_prompts[agent_role]` → `active_system_prompt` (fallback) |

**The sound-conservative binary same-prefix predicate (computable at the CP fan-out site):**

> All branches are in the same cohort **iff** they are uniform in **`(binding.agent_role, binding.prompt_version_sha)`** across the `branch_plan`, AND cap > 1.

- Uniform `agent_role` + uniform `prompt_version_sha` ⟹ identical `system_prompt` resolution (same role → same per-role lookup or same fallback; same override → same content). Combined with the construction-shared `frozen_tool_superset` ⟹ **identical prefix**. `[HIGH]`
- **Soundness:** the predicate can only be a FALSE-NEGATIVE (two different roles that happen to map to identical prompt content are treated as different cohorts → miss the optimization → all-concurrent). That is a *safe miss* (no correctness impact — just a foregone cache-hit), never a false-positive (never serializes non-cohort siblings). `[HIGH]`
- **Why NOT the full hash here:** computing `prefix_content_hash = sha256(canonical(frozen_tool_superset) ‖ version_sha)` (slice-3b DDR §4.1) is only needed to *partition* a heterogeneous fan-out into K cohorts. The homogeneous slice is the degenerate single-cohort case — a binary "are they all the same?" suffices and dodges the hash entirely (findings §Correction). `[HIGH]`
- **Constraint noted:** `frozen_tool_superset` is NOT visible at the CP driver (it lives inside `RuntimeLLMDispatcher`; CP treats the dispatcher as an opaque `StepDispatcher` Protocol). The predicate does NOT need to read it — it relies on the *construction invariant* that all siblings share the one dispatcher's superset. The **opt-in gate** (below) is the operator's assertion that a cacheable prefix exists worth warming. `[MODERATE — rests on the shared-dispatcher construction invariant; verify at build that all PARALLELIZATION branches route to the same dispatcher instance.]`

---

## 3. Gate carrier — three options, recommend the D4 tunable

The serialize-`branch[0]` DECISION is made in `_execute_parallelization` (`workflow_driver.py:6681`). It needs (a) an opt-in flag and (b) the same-prefix predicate inputs (the `binding`s, already in `branch_plan`). The flag must arrive through the signature. `DriverContext` is a **Protocol** (`workflow_driver.py:455`) — adding a member is a broad structural change to all implementers, so it is dispreferred. Three real carriers:

| Option | Carrier | Pros | Cons |
|---|---|---|---|
| **A (RECOMMEND)** | New field `concurrent_cache_warmup: bool = False` on the **D4 multiplicative tunable** (resolved via `d4_tunable(...)` at `workflow_driver.py:6897`) | Architecturally coherent — ADR-D4 §1.8 IS a per-cell topology property ("applies to all cells where fan-out cap > 1"); threads exactly like `cascade_policy`; already per-(workload-class × engine-class) | CP-spec touch (C-CP-11 / §25.15 D4 tunable schema); the tunable defaults table needs the new field |
| B | New field on `WorkflowManifestEntry` | Per-workflow operator control | C-CP-05 schema change; less coherent (warm-up is a topology-cell property, not a whole-workflow one) |
| C | New `cohort_key()` method on the `StepDispatcher` Protocol | Encapsulates the prefix hash in the runtime dispatcher (needed anyway for 3c-full) | Protocol widening (C-CP-25 §25.3.3.4 / C-RT-15); over-built for the homogeneous slice (which needs only the binary predicate, not the hash) |

**Recommendation: Option A.** It matches the ADR's own per-cell framing and reuses the exact `d4_tunable` threading that already delivers `cascade_policy` to this function. Option C becomes attractive *later* for 3c-full (it's the natural home for the cohort hash), so it is a registered generalization, not a rejection. `[MODERATE — advisor should sanity-check A-vs-C given C is the eventual 3c-full home; A may be re-worked into C at 3c-full. Counter-argument: A is additive and cheap now; C's rework is a field-move, low cost.]`

---

## 4. The ADR-required vs guardrail-opt-in tension (nameable, pre-resolved)

- **The tension** (nameable, C6/C1 ⊥ C11): ADR-D4 §1.8(f) says warm-up is **required** at cap > 1 (C6 cost-amortization / C1 orchestration). The findings §Correction build-guardrail says **opt-in, default OFF** (C11 operator-loop / local-deployment: don't silently change fan-out concurrency behavior). `[HIGH]`
- **Resolution (pre-resolved by the ratified guardrail — `[[probe-resolves-fork-prescribed-council]]`):** ship **opt-in default-OFF** for this first slice. The default path stays **byte-identical** (all-concurrent) while the mechanism is proven end-to-end. Flipping the default to the ADR's required-at-cap>1 is a **registered follow-on** (`B-18-3C-PREWARM-DEFAULT-ON`), gated on the witness suite + a live cache-hit e2e. No council needed — the guardrail already adjudicates. `[HIGH]`
- This mirrors the slice-3b ttl opt-in precedent (`prompt_cache_long_ttl_workloads`, default empty → byte-identical). `[HIGH]`

---

## 5. Integration point — reuse `_proceed_branch`, PROCEED path only

### 5.1 The grounded fan-out structure (re-verified this session, not from the subagent summary)

- `_execute_parallelization` (`workflow_driver.py:6681`) builds `branch_plan: list[(branch_index, step, child, writer, binding)]` (element assembled at `:7067`). `[HIGH]`
- **PROCEED path:** `_proceed_fanout()` (`:7535`) runs `asyncio.gather(*(_proceed_branch(*plan) for plan in branch_plan))` (`:7539-7540`), wrapped by `_run_fanout_to_completion` (`:6223`, a dedicated event loop + `ThreadPoolExecutor`). `[HIGH]`
- **CASCADE_CANCEL / PAUSE path:** `_cancel_fanout()` (`:7752`) runs under `cascade_cancel_barrier` (`:2067`, `asyncio.TaskGroup` structured cancellation, task creation at `:2157`). `[HIGH]`
- **Per-branch completion is self-contained** — `_record_clean` (`:7313-7354`) does, per branch: `append_branch_step_ledger_entry` → **`_replay_store.record_branch(...)`** (RESERVE-before-COMMIT; the SOLE crash-resume which-branches-completed authority, `:7340-7344`) → `append_branch_terminal_ledger_entry` → `collected[bi] = (step_id, output)` → `terminal_dispositions[bi] = "completed"`. `[HIGH]`

### 5.2 The insertion (PROCEED path)

```python
async def _proceed_fanout() -> list[Any]:
    if _warmup_gate:                       # d4 tunable ON ∧ cap>1 ∧ same-prefix cohort
        first = await _proceed_branch(*branch_plan[0])           # serialize: cache-write
        rest = await asyncio.gather(
            *(_proceed_branch(*plan) for plan in branch_plan[1:]),  # release: cache-hits
            return_exceptions=... )
        return [first, *rest]
    return await asyncio.gather(*(_proceed_branch(*plan) for plan in branch_plan), ...)  # default
```

**Why this is safe — it preserves every invariant with zero new bookkeeping:** `[HIGH]`
- `_proceed_branch` is the *identical* coroutine used today; running `branch_plan[0]` through it first just orders it before the rest. Per-branch ledger entries, the replay-store `record_branch`, effect-fence resolution (already resolved pre-barrier at `:6999-7033`), the drain buffer, `collected`, and `terminal_dispositions` are all produced by `_proceed_branch` itself — no parallel hand-rolled path (this is the hazard the subagent's "dispatch outside the barrier" sketch introduced; reusing `_proceed_branch` avoids it).
- **Result ordering preserved:** `[first, *rest]` matches `branch_plan` order, so the deterministic aggregate/voting/tiebreak (branch-index order) is unchanged.
- **Crash-resume-mid-warm is naturally correct:** `branch[0]`'s `record_branch` durably lands (RESERVE-before-COMMIT) BEFORE `branch[1..N-1]` start. A crash after `branch[0]` warmed → resume reads the store, seeds `branch[0]` as `completed` (`:7167-7175`), re-dispatches only `[1..N-1]`. This is NOT a new resume case — today ANY completed subset can be recovered; serialization just makes `branch[0]-first` a deterministic ordering the existing arbitrary-subset resume already handles. `[HIGH]`

### 5.3 Cascade-policy scope — PROCEED only (first slice)

Apply the warm-up **only when `cascade_policy is CascadePolicy.PROCEED`**; leave CASCADE_CANCEL and PAUSE **byte-identical** (all-concurrent). Rationale: `[MODERATE]`
- PROCEED is the research / lossy-synthesis / read-heavy fan-out regime ADR-D4 §1.8 explicitly targets (Cluster 1 §[HIGH] Anthropic research system), and it has **no cross-sibling cancellation** — the simplest, lowest-risk interaction.
- CASCADE_CANCEL/PAUSE serialization is *feasible* (branch[0] serialized before the TaskGroup; on branch[0] failure, skip the TaskGroup and drive the cascade/snapshot for the un-dispatched `[1..N-1]`) but touches the TaskGroup + snapshot-build (`:7898`) + the `not branch_plan` re-establish paths — a materially larger review surface for the same cache benefit. **Registered follow-on `B-18-3C-PREWARM-CASCADE`.**
- The opt-in gate already restricts to same-prefix cohorts; further restricting to PROCEED is conservative and reversible.

---

## 6. Test plan (reuse the existing fan-out scaffolding — the empirical safety net)

Scaffolding from `harness-cp/tests/test_workflow_driver_parallelization.py` (`_manifest`, `_DEFAULT_BINDING`, `_ACTOR`) + a fake dispatcher counting prompt-cache **writes vs hits** (mirror the `test_cacheable_epoch_ttl_slice3b.py` fake-client cache-counting pattern). `[HIGH]`

1. **Witness (the load-bearing by-execution proof):** warm-up ON + same-prefix + cap N → **1 cache-write + (N-1) cache-hits**; baseline (OFF) → **N cache-writes** (the miss storm). `[[full-chain-witness-not-half-proofs]]`.
2. **Ordering:** `branch[0]` completes before `branch[1..N-1]` begin (assert dispatch timestamps / a recorded start-order).
3. **Heterogeneous → all-concurrent:** branches with differing `agent_role` (or a per-step `prompt_version_sha` override) → predicate false → no serialization (safe miss).
4. **Opt-in OFF → byte-identical:** default path unchanged vs the current all-concurrent baseline (aggregate + ledger + ordering identical).
5. **Crash-resume after `branch[0]`:** crash after `branch[0]` recorded, before `[1..N-1]` dispatched → resume re-dispatches only `[1..N-1]`; `branch[0]` output recovered from the replay store; aggregate correct.
6. **Non-PROCEED untouched:** CASCADE_CANCEL + PAUSE fan-outs with warm-up ON → still all-concurrent (byte-identical), cascade/pause/snapshot semantics unchanged.
7. **Regression sweep:** the full existing fan-out suite must stay green — `test_workflow_driver_parallelization{,_pause}.py`, `_fanout_output_replay{,_full_chain}.py`, `_fanout_pause.py`, `_cascade_policy.py`, `_effect_fence_pause.py`, `_drain.py` (the ~600KB net that catches any effect-fence/cascade/crash-resume/drain breakage).
8. **Live cache-hit e2e** (paid-gate, `@pytest.mark.e2e`, NOT fired autonomously): real Anthropic fan-out shows `cache_read_input_tokens > 0` on siblings `[1..N-1]`.

---

## 7. Spec + clearance surface

- **CP spec** (bundled absorption): add `concurrent_cache_warmup` to the D4 multiplicative tunable (C-CP-11 / §25.15), materializing ADR-D4 §1.8 steps 2-4 at the WorkflowDriver PARALLELIZATION path. Note the opt-in-default-off staging + the PROCEED-only first scope. `[MODERATE]`
- **No IS/runtime cohort-hash** for this slice (the binary predicate suffices). `[HIGH]`
- **Clearance marker** for the CP spec bump. Decorrelated review = out-of-family `just codex-review` + main-agent review (advisor when available). `[HIGH]`

---

## 8. Deferred / registered follow-ons (SPINE `B-*`)

| Follow-on | Scope | Why deferred |
|---|---|---|
| `B-18-3C-PREWARM-CASCADE` | warm-up on CASCADE_CANCEL + PAUSE paths | TaskGroup + snapshot interaction; larger review surface, same benefit |
| `B-18-3C-PREWARM-DEFAULT-ON` | flip the D4-tunable default to ADR §1.8(f) required-at-cap>1 | gated on the witness suite + live cache-hit e2e proving the mechanism |
| `B-18-EPOCH-PARTITION` (3b-epochkey + 3c-full) | the `version_sha` cohort HASH + heterogeneous partition (warm one per cohort) | needed only for heterogeneous fan-out; the binary predicate covers homogeneous |
| `B-18-KEEPALIVE` (R2) | boot-time `max_tokens=0` pre-warm + every-4min keep-alive (ADR-D3 §1.5 lines 189-190) | distinct mechanism; C11-safe default opt-in-off |
| `B-18-LANEB-PROMPT-SEMVER` | operator-declared semantic-version field on `PromptVersion` | IS-spec amendment; NOT required (version_sha is the cache key) |

---

## 9. Open questions for advisor / operator review (before build)

1. **Gate carrier A-vs-C** (§3): D4-tunable field now, or go straight to the `StepDispatcher.cohort_key()` Protocol method (the eventual 3c-full home) to avoid a later field-move? Recommendation: A (cheap, additive, coherent now); accept the small later rework.
2. **PROCEED-only scope** (§5.3): acceptable first cut, or does the operator want CASCADE_CANCEL/PAUSE in the first slice?
3. **Shared-dispatcher construction invariant** (§2): confirm at build that all PARALLELIZATION branches route to the same `RuntimeLLMDispatcher` instance (so the shared-`frozen_tool_superset` assumption holds). If per-branch dispatchers can differ, the predicate must also assert dispatcher identity.
4. **Opt-in default-off** (§4): confirm the staged rollout (vs honoring ADR §1.8(f)'s required-at-cap>1 immediately). Recommendation: opt-in first, per the ratified guardrail.

---

## 10. Grounded code-surface index (exact refs, re-verified this session)

| Surface | Ref |
|---|---|
| PARALLELIZATION strategy | `harness-cp/src/harness_cp/workflow_driver.py:6681` `_execute_parallelization` |
| PROCEED barrier | `:7535` `_proceed_fanout` → `asyncio.gather` `:7539-7540` |
| CASCADE/PAUSE barrier | `:7752` `_cancel_fanout` → `cascade_cancel_barrier` `:2067` (TaskGroup `:2157`) |
| fan-out runner | `:6223` `_run_fanout_to_completion` (dedicated loop + ThreadPoolExecutor) |
| per-branch record (crash-resume authority) | `:7313-7354` `_record_clean` → `_replay_store.record_branch` `:7340-7344` |
| branch_plan tuple | `:7067` `(branch_index, step, child, writer, binding)` |
| cascade_policy resolution | `:6897-6900` `d4_tunable(...).cascade_policy` |
| crash-resume seed | `:7167-7175`; determine at `:6322` `_determine_fanout_resume` |
| effective system-prompt resolution | `harness-runtime/.../llm_dispatch.py:1005-1037` |
| frozen_tool_superset field (NOT visible at CP) | `llm_dispatch.py:579`; select at `:1320-1337` |
| DriverContext (Protocol) | `workflow_driver.py:455` |
| ttl opt-in precedent | `harness-runtime/.../types.py:1859` `prompt_cache_long_ttl_workloads` |
| ADR design | `design-substrate/ADR-D4.md:228-240` (§1.8) |
| cohort hash (3c-full, deferred) | `.harness/u1-slice3b-epoch-partition-design.md` §4.1 |
| build guardrails | `.harness/u1-slice3-findings-and-f1-c10-gap.md` §Correction |
| fan-out test net | `harness-cp/tests/test_workflow_driver_parallelization{,_pause}.py`, `_fanout_output_replay{,_full_chain}.py`, `_fanout_pause.py`, `_cascade_policy.py`, `_effect_fence_pause.py`, `_drain.py` |

---

*End DDR. Next session: advisor-review §9 open questions → build §5 (PROCEED, opt-in-off) with §6 tests → CP-spec + clearance → codex-review → PR → refresh.*
