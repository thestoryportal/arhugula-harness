# Class 1 (design) — Nested paused-child HITL-response routing: value-threaded `resume_context`, not a keyed shared map (B-39)

**Status:** ✅ RATIFIED 2026-07-23 (operator `AskUserQuestion`, same-day as filing) — **Q1 = (A) retire `ResumeContextHolder` entirely; Q2 = (A) batched map at the API boundary.** Both are the heavier of the offered readings — Q2 in particular is the genuine public-API expansion this fork flagged as crossing the X-AL-3 line, so the spec+impl arc is now larger than the minimum, not smaller. No code has landed yet; per the B-33/B-59 precedent, this ratification opens a **spec leg** (CP §26 + Runtime §14.8 deltas + clearance markers + plan units) as its own arc, followed by a separate **impl leg** (code + tests) — not bundled into one PR. Two carried-forward risks for the spec/impl legs to resolve precisely, not hand-wave: (1) retiring `ResumeContextHolder` removes a primitive the effect-fence-pause-resolution `peek()` reader (`workflow_driver.py:~4503`) depends on — needs its own by-execution test after migration; (2) the batched-map resolution semantics (how `Mapping[branch_path, ResumeContext]` routes to a recursion level, what depth-0's own key is, what happens on a map entry matching no paused child) is the part the spec delta must pin down, not leave implicit in code.

**Posture:** design-phase back-flow. Touches CP spec §26 (`execute_workflow` contract, `ResumeContext`/`PausedChildBranchResumeState` carriers) + Runtime spec (`api.resume()` public surface, `ResumeContextHolder` sidecar lifecycle). Two genuine architecture decisions below are operator-gated (Q1, Q2); everything else is a mechanical consequence of the grounding.

---

## 0. Why this fork exists (register lineage)

`B-32` (nested pause-REASON propagation) closed 2026-07-15 — a parent correctly reports `HITL_PENDING` when a nested child paused for a HITL gate. `B-39` split off the harder half: **delivering** each paused child its own correct operator response. A first attempt (keyed `dict[workflow_id, HITLResult]` + non-destructive `peek()`, mirroring the `effect_fence_resolutions` per-branch pattern) was built, mutation-probed, and reverted after out-of-family Codex found 3 real defects before it shipped:

1. **Never one-shot-consumes** — `peek()` never clears a keyed entry; a later unrelated step sharing the same key would silently reuse a stale response.
2. **`workflow_id` is not branch-unique** — fan-out siblings can legitimately dispatch the SAME `child_workflow_id`; the runtime already uses `branch_path` for exactly this disambiguation elsewhere.
3. **The delivery mechanism itself is unresolved** — `execute_workflow`/child re-entry has no `resume_context` parameter at all; the "mirror effect-fence" premise doesn't actually carry into a recursive child's own re-entry.

This fork addresses (3) directly, and shows (1)+(2) are **structurally foreclosed** (not just patched) once (3) is solved the way §2 proposes.

## 1. The crux — the singleton isn't the map shape, it's the DELIVERY substrate

Grounded directly at HEAD (`0d302599`):

- `ResumeContextHolder` (`harness-runtime/.../lifecycle/resume_context_holder.py`) is ONE mutable sidecar hung off `HarnessContext`/`ctx` — `_current_context: ResumeContext | None`, consumed via `consume_and_clear()` / `peek()` (the latter used by the effect-fence-pause-resolution reader, `workflow_driver.py:4503-4508`).
- `ctx` (the `DriverContext`) is threaded **identically, by reference, to every recursion level** — `_execute_orchestrator_workers`/`_execute_hierarchical_delegation`/`_execute_parallelization` all pass the SAME `ctx` down to every worker's recursive `execute_workflow(..., ctx=ctx, ...)` call. So today there is exactly **one** `ResumeContext` slot for an entire recursive run tree, at any depth — the map-shape the reverted attempt built sat ON TOP of this single-slot substrate, which is why it needed non-destructive `peek()` in the first place (a destructive consume would have raced the top-level gate for the same slot).
- `api.resume()` (`harness-runtime/.../api.py:715`) mirrors this at the public surface: `resume_context: ResumeContext | None = None` — **singular**, one per call, "delivered one-shot to the resumed-step gate" (docstring, singular "the resumed-step gate" — no per-child addressing exists).
- The recursion DOES already correctly disambiguate per-child state for the pause-snapshot half: `PausedChildBranchResumeState.child_snapshot` is threaded as `execute_workflow(pause_snapshot_input=child_snapshot)` at the exact worker re-dispatch site (`pause_resume_protocol_types.py:741-780`), keyed positionally by `branch_index`/`step_id` (+ `child_workflow_id` since B-31). **`resume_context` has no equivalent parameter to ride the same plumbing.**

So the reverted attempt's diagnosis was one layer too shallow: the bug isn't "the map is keyed wrong," it's "there's no per-call parameter for a keyed value to flow through in the first place" — the map was bolted onto a shared-mutable-state substrate that was never designed to carry more than one value.

## 2. The proposed design — thread `resume_context` BY VALUE through the existing `pause_snapshot_input` plumbing

Mirror the mechanism that already works correctly for `pause_snapshot_input`, rather than inventing a second (keyed-map) mechanism next to it.

1. **Add `resume_context: ResumeContext | None = None` to `execute_workflow`'s signature**, positioned identically to `pause_snapshot_input` (same call-site pattern; same "recurses for free" property — every existing recursive call site already threads `pause_snapshot_input` positionally per-child, so the new parameter travels the same wires).
2. **At each worker resume re-dispatch site** (`_execute_orchestrator_workers` / `_execute_hierarchical_delegation` / `_execute_parallelization`, the exact place that resolves `PausedChildBranchResumeState.child_snapshot` today), thread `resume_context=<this branch's resolved ResumeContext>` alongside `pause_snapshot_input=child_snapshot`. The resolution of "which value belongs to this branch" happens ONCE, at the API boundary (§2 point 4 / Q2) — not re-solved at every recursion level.
3. **Inside `execute_workflow`, the resumed-step HITL gate composer consumes the PASSED-IN parameter directly** for this call's own resumed step, instead of reading `ctx.resume_context_holder.consume_and_clear()`. A function parameter, scoped to one `execute_workflow` invocation and never stored past it, satisfies one-shot delivery **by construction** — defect (1) (never-one-shot-consumes) cannot recur because there is no persistent slot left to go stale.
4. **Branch-uniqueness (defect 2) is closed the same way**: the value rides the SAME recursive call that already correctly disambiguates fan-out siblings via `branch_index`/`step_id`/`child_workflow_id` (B-31's guard). No keyed map is needed at any consumption site — "which child does this response belong to" is answered once, by the caller, at the point where it already has the answer (the branch it's re-dispatching).

This is a **type-driven** fix in the CLAUDE.md §4 sense: the shared-mutable-singleton was the bug (a second, implicit source of truth alongside the already-correct `pause_snapshot_input` threading); replacing it with a plain per-call value closes both concrete defects as a side effect of removing the bad primitive, not as separately-patched logic.

## 3. Two genuine architecture decisions (operator-gated)

**Q1 — does the top-level (depth-0) pause ALSO migrate off `ResumeContextHolder`, or keep it?**

Two readings:
- **(A) Retire the holder entirely.** Depth-0 becomes "recursion level zero" like any other — `api.resume()`'s existing single `resume_context` becomes the depth-0 call's `execute_workflow(resume_context=...)` argument, same code path as every nested level. One mechanism top-to-bottom; the `peek()` consumer at `workflow_driver.py:4503` (effect-fence-pause-resolution) needs its own read-path updated to the new parameter (it currently reads the holder directly via `getattr(ctx, "resume_context_holder", None)`).
- **(B) Keep the holder for depth-0, add the new parameter only for nested re-entry.** Smaller diff, but leaves two delivery mechanisms live side-by-side for what is conceptually one concept (an operator response reaching a paused gate) — a `[[carrier-home-defect-pattern]]`-adjacent smell (same concept, two carriers) that would need its own future reconciliation.

**Recommendation: (A).** It is the smaller total surface (one mechanism, not two-that-must-stay-in-sync) and directly resolves the `peek()` special-case's justification (peek existed specifically to avoid destructively racing the SAME slot against two different in-holder readers — a per-call parameter has no such race by construction).

**Q2 — how does `api.resume()` accept MULTIPLE per-child responses in one call, when 2+ children are concurrently paused for different reasons?**

Three readings:
- **(A) Batched map at the API boundary.** Extend `resume()`'s public signature to `resume_context: ResumeContext | Mapping[str, ResumeContext] | None` keyed by `branch_path` (the same stable per-branch identity `compose_branch_path` already produces at §25.16) — one `resume()` call delivers responses to every currently-paused child at once. Requires a CP spec delta (§26 resume contract) + a Runtime spec delta (`api.resume()` signature) + a new resolver at the top of `execute_workflow`'s resume path that fans the map out to the right recursion level by `branch_path` prefix-match.
- **(B) One `resume()` call per outstanding child.** Keep `resume_context` singular; add a new `target_branch_path: str | None` parameter so the caller names WHICH paused child this call's response is for (today `resume()`/`attempt_resume` has no targeting parameter at all — an ambiguous multi-child pause would have nowhere to route a singular response). The caller loops, one call per outstanding child, each re-pausing on the remaining ones until all are answered.
- **(C) Don't build multi-child delivery yet.** Ship §2's mechanism (which is a strict improvement even for the single-paused-child case — it closes defects 1+2 regardless), but leave 2+-concurrently-paused-children-of-different-reasons explicitly unsupported/undefined until a real deployment scenario is confirmed reachable (today's fixtures exercise nested PAUSE via plain branch-failure cascades, not concurrent HITL gates — per the B-39 register's own "not urgent" framing at `.harness/post-phase-8-forward-register.md`).

**No recommendation held back on principle** — (A) is architecturally cleanest and matches the workspace's existing `branch_path`-keying precedent, but it is a real public-API surface expansion (a committed-behavior change to `api.resume()`, CP-spec-owned) crossing the exact line X-AL-3 exists to gate. (C) is the lowest-risk, ships §2's clean single-child mechanism now and defers the multi-child API question until it has a live trigger — consistent with how `B-44`/`B-45` were deliberately left registered-not-built for the same reason (no demonstrated consumer yet).

## 4. Impl surfaces (once Q1/Q2 are ratified)

| Surface | Change |
|---|---|
| `harness-cp/.../workflow_driver.py` — `execute_workflow` | NEW `resume_context: ResumeContext \| None = None` param; resumed-step HITL gate composer reads it instead of (or in addition to, per Q1) `ctx.resume_context_holder` |
| `harness-cp/.../workflow_driver.py` — worker resume re-dispatch (`_execute_orchestrator_workers` / `_execute_hierarchical_delegation` / `_execute_parallelization`) | thread `resume_context=<resolved per-branch value>` alongside the existing `pause_snapshot_input=child_snapshot` |
| `harness-cp/.../workflow_driver.py:4503` (effect-fence `peek()` reader) | IF Q1=(A): re-point at the new parameter; the `peek()`-vs-`consume_and_clear()` non-contention rationale needs re-verifying under the new shape |
| `harness-runtime/.../lifecycle/resume_context_holder.py` | IF Q1=(A): retire (or narrow to a depth-0-only compatibility shim); IF Q1=(B): unchanged |
| `harness-runtime/.../api.py` — `resume()` | IF Q2=(A): new `Mapping[str, ResumeContext]` overload/union + `branch_path` resolver; IF Q2=(B): new `target_branch_path` param; IF Q2=(C): unchanged this arc |
| `design-substrate/Spec_Control_Plane_v1_105.md` §26 | `execute_workflow` contract delta (new param); Q2=(A)/(B) resume-contract delta |
| `design-substrate/Spec_Harness_Runtime_v1.md` §14.8 | `api.resume()` signature delta (Q2=(A)/(B) only); `ResumeContextHolder` retirement note (Q1=(A) only) |
| clearance markers | CP + Runtime, per §4.5, once ratified |

## 5. What this fork does NOT resolve

- The original council framing (C7/C8 HITL-fidelity vs C1/C5 orchestration-correctness) is not re-opened here — per the register's own `[[probe-resolves-fork-prescribed-council]]` discipline, the concrete mechanism above is probed/grounded first; no cross-domain value tension surfaced during grounding (both readings at Q1/Q2 are engineering-tradeoff forks, not value forks), so council convening is NOT recommended unless the operator's own answer to Q1/Q2 surfaces one.
- Whether a real multi-child-concurrent-HITL-pause scenario is reachable in a live deployment today is unchanged by this doc — it remains unconfirmed (register text, still accurate at this grounding pass).

## 6. Grounding leads (verified at HEAD `0d302599`)

`resume_context_holder.py` (full file, 91 lines); `pause_resume_protocol_types.py:880-940` (`ResumeContext`), `:741-793` (`PausedChildBranchResumeState`); `workflow_driver.py:2687-2698` (`execute_workflow` signature), `:4060-4098` (`HIERARCHICAL_DELEGATION` recursive dispatch), `:4503-4510` (effect-fence `peek()` reader); `api.py:715-770` (`resume()` public signature + docstring); `.harness/forward-register.yaml` B-39 row (re-grounded 2026-07-15); `.harness/post-phase-8-forward-register.md` §B-39 (3-defect record on the reverted attempt).
