# Implementation Plan: Control Plane — v2.48 (delta over v2.47)

*v2.48 is the CP plan leg of register row **`B-100`**'s spec leg, absorbing **CP spec v1.112 → v1.113** (ONE amendment site: §2.1's empty-`idempotency_key` key-ABSENT treatment, generalized from a **PROVENANCE** scope to a **STATE** scope, adding a KEY-ABSENT sibling SOURCE SHAPE for the LINEAR and orchestrator carriers). **ONE EXISTING unit is amended — U-CP-64**, which v2.47 §0.3 established as the owner of both the `ResumeContext` carrier and the §2 projection surface. **ZERO new units; ZERO new cluster; ZERO DAG topology change of any kind — within CP or cross-axis.** The variant set is unchanged at FOUR, so no new classification, resolver, or carrier obligation arises; the delta widens the SOURCE column of a surface U-CP-64 already owns. This is the SPEC LEG's plan absorption only — impl (code + tests) is a separate follow-on arc per the `B-33` / `B-39` / `B-59` / `B-69` / `B-70` / `B-72` / `B-97` precedent.*

**Status:** Proposed

---

## §0 Change-note (v2.47 → v2.48)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_47.md` (v2.47 — the RATIFIED `B-69` arc's CP plan leg; ONE amended unit (U-CP-64), zero new units).

### §0.2 Revision context

CP spec v1.113 §1 generalizes v1.112 §2.1's key-ABSENT treatment: **any effect-fence source shape whose captured `idempotency_key` is EMPTY carries NO key field**, which adds a KEY-ABSENT sibling source shape for the LINEAR `EffectFenceResumeState` and for `OrchestratorEffectFencePausedResumeState` alongside the one the branch carrier already had. `effect-fence-addressable` therefore spans **SIX** source shapes (was FOUR) and the union spans **TEN** (was EIGHT), across an **UNCHANGED SEVEN** distinct source carriers. **The VARIANT set remains FOUR.**

**Why this is a plan delta at all, given the variant set is unchanged.** `[HIGH]` The two new shapes are **not** materialized by the shipped surface: `walk_pause_tree` constructs `LinearEffectFenceAddressableLocation` (`harness-cp/src/harness_cp/pause_state_projection.py:509`) and `OrchestratorEffectFenceAddressableLocation` (`:522`) **unconditionally** from the carrier's key, with no emptiness routing — so an empty key at either is surfaced today as a `""` key **value**, precisely the state v1.113 §1.1 forbids. The branch shape already has its routing helper (`_effect_fence_branch_projection`, `:621`–`:649`). **An acceptance criterion is therefore owed, or the impl leg has no criterion to build to.**

### §0.3 Why U-CP-64, and why an ADDED criterion rather than an amended one

**U-CP-64 owns the §2 projection surface** — established at v2.47 §0.3 on the ground that the projection's four variants are the carrier's own addressing space published. v1.113 amends that same surface. The owner is unambiguous and unchanged.

**AC #A11 is ADDED rather than #A4 being rewritten.** AC #A4's crash-reconstruction clause remains **true as written** — the branch carrier holding an empty key still projects with the key field ABSENT; it is now a *special case* of the general rule rather than the whole of it. Rewriting a preserved acceptance criterion to restate a superset would churn a witness the `B-69` impl leg already landed green. **All of AC #A1 … #A10 are PRESERVED VERBATIM.**

### §0.4 Cross-axis cascade — NONE NEW, determined rather than assumed

The Runtime-side DTO that consumes this surface is `U-RT-148` (`Implementation_Plan_Harness_Runtime_v2_57.md` §1), and the **U-RT-148 → U-CP-64 edge already exists**, declared at v2.47 §0.4. This delta adds **no new edge, no new crossing point, and no new consumer**; the already-crossing structured sequence gains two source-shape members. **CXA determination: `Cross_Axis_Composition_Document_v2_23.md` is UNCHANGED, aggregate FROZEN at 111** — same boundary, same consumers, payload widening only, on the same ground the `B-69` leg recorded. *(Stated explicitly rather than as a blanket "zero cascade", per the correction v2.47 §0.5 itself carries.)*

### §0.5 What this delta does NOT do

- It does **NOT** add a unit, a cluster, or a DAG edge — within CP **or** cross-axis.
- It does **NOT** amend AC #A1 … #A10, or any unit owning §1.2 properties 1–5 / §1.1 properties 6–8. Those are **PRESERVED VERBATIM**; v1.113 adds no classification rule.
- It does **NOT** add a capture-side obligation. `B-100`'s disposition **(b)** (refusing an empty key at the capture sites) is **NOT** applied — its own close-out declines it as hash-adjacent, and CP spec v1.113 §2 records that. **No carrier gains a length constraint; `snapshot_hash` is untouched.**
- It does **NOT** close the SCALAR uniform-fallback channel, and that limit is **REGISTERED as `B-106`**, not assumed away. AC #A11 constrains the **projection**; it cannot constrain `resume_context.effect_fence_resolution`, a scalar the caller sets independently. `compute_effect_fence_uniform_fallback_eligible_key` (`workflow_driver.py:2935`–`:2970`) does not filter empty keys, so a key-absent LINEAR fence that is the sole unaddressed location can still receive a uniform resolution that the runtime never matches. **Closing it needs a CP classification-rule change (forbidden to §2 by v1.112 §2.4), the declined capture-side disposition (b), or a refuse-at-the-seam change to the resume path's failure mode** — none is in this delta's authorized scope, and `B-106`'s close-out grounds the three against each other (the resolver-side option has **no** liveness cost but produces no **refusal**). **Do NOT read AC #A11 green as evidence that channel is closed.**
- It does **NOT** add a deferred coverage-matrix row. v2.47 §2's reasoning holds unchanged: this surface has an **owner**, and a deferred row alongside an assignment would double-book it.

---

## §1 U-CP-64 amendment — the KEY-ABSENT sibling source shapes

**Unit ID:** U-CP-64 (EXISTING — amended, not re-decomposed)
**Spec anchors:** `Spec_Control_Plane_v1_113.md` §1 (amending `Spec_Control_Plane_v1_112.md` §2.1); consumed cross-axis by `Spec_Harness_Runtime_v1.md` v1.109 §14.14.9.2
**Prior amendments preserved:** v2.21 (original `ResumeContext` authoring), v2.42 (`hitl_responses` / `hitl_response_for`), v2.47 (the `B-69` provenance carrier + the projection surface). **All prior U-CP-64 acceptance criteria — including AC #A1 … #A10 — are PRESERVED VERBATIM**; the criterion below is ADDED.

### §1.1 Added scope

The projection routes **every** effect-fence source carrier by the **STATE of its captured key**, not by provenance: a captured `idempotency_key` that is empty yields a **KEY-ABSENT sibling source shape carrying no key field at all**, for the LINEAR and orchestrator carriers exactly as it already does for the branch carrier. Each key-absent shape carries its carrier's existing field set **minus the key** — **no `step_kind` capture is added anywhere**, and no carrier is retyped.

### §1.2 Added acceptance criterion

**AC #A11 — the KEY-ABSENT sibling source shapes, for ALL THREE effect-fence carriers, witnessed by DETECT-THEN-REFUSE.** `[HIGH]`

**(a)** Construct a snapshot whose LINEAR `EffectFenceResumeState` carries `idempotency_key=""`; assert the projection classifies it **`effect-fence-addressable`** with the key field **ABSENT** — never a `""` key value, never omitted from the enumeration.

**(b)** The same for `OrchestratorEffectFencePausedResumeState` carrying `idempotency_key=""`.

**(c)** Assert **unrepresentability, not merely absence**, in **BOTH directions and over BOTH failure shapes**: assert by test that (c1) the key-absent projection types **cannot be constructed carrying a key**; (c2) the key-bearing ones **cannot be constructed carrying an EMPTY key**; and (c3) the key-bearing ones **cannot be constructed with the key OMITTED**. *(c3) is not redundant with (c2) and its omission was caught at out-of-family review round 5 [P1]:* an implementation using one key-bearing type with an **optional but length-constrained** field passes (c2) — it does reject `""` — while still admitting a key-bearing projection with **no key at all**, which is exactly the illegal state this union exists to close, and which the sibling Runtime criterion (`Implementation_Plan_Harness_Runtime_v2_57.md` AC #15(b)) already forbids. **Assert the refusals, not merely that the happy paths work** — an absence-only assertion cannot tell a type invariant from a happens-to-be-`None` (v1.113 §1.4).

**(d)** Assert the branch carrier's existing behaviour is **UNCHANGED** — AC #A4's crash-reconstruction witness re-runs green, unmodified. *It is now a special case of the general rule, not a separate rule.*

**Two constraints on how (b) is witnessed, stated so a later reviewer does not read a correct test as an inadequate one.** `[HIGH]`

1. **(b) MUST be a CONSTRUCTED-SNAPSHOT test, never an end-to-end run.** The orchestrator carrier's sole shipped capture site (`harness-cp/src/harness_cp/workflow_driver.py:12392`) guards on a **truthy** key at `:12376`–`:12381`, so **no production path can produce this state** — the shape is declared on TYPE-TOTALITY grounds (the carrier type admits `""`, and the projection is a total function over journaled records that outlive the capture-site code). *Register row `B-100` asserted the opposite of that guard's presence; the premise was checked at the spec leg and found FALSE — see `Spec_Control_Plane_v1_113.md` §0.4 finding (i). The disposition is unchanged; only its ground is.* **An acceptance closeout that demands an e2e witness for (b) is demanding an unbuildable one.**
2. **(a) is reachable and MUST NOT be downgraded to (b)'s posture.** The LINEAR capture site constructs its carrier whenever the runtime error's `idempotency_key` attribute `isinstance(_, str)` (`workflow_driver.py:5456`), which **admits `""`**. Its exposure is defensive rather than a known live defect, but the state is genuinely reachable and the witness may be driven through the capture site.

### §1.3 The mechanism the criterion protects, stated once so the impl leg does not re-derive it

`[HIGH]` A `""` key surfaced as a key **value** is an address the resume path never honours, and the mechanism differs by site — the impl leg should not assume the single mechanism `B-100` names. At the **fan-out per-branch** dispatch sites **and at the ORCHESTRATOR consult** (`workflow_driver.py:12118`) the consult is **gated on a truthy key**, so an empty key is never consulted at all. At the **LINEAR** consult ALONE (`workflow_driver.py:4925`–`:4936`) the resolution IS looked up, but the resulting directive is applied only when the runtime's **recomputed** per-`(run, step, tool)` dispatch key equals it (`harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:1042`, against the key composed at `:989`) — never `""` — so it is threaded and then discarded and the dispatch re-pauses INERT. And `compute_effect_fence_tree_wide_abort_present` filters all empty keys before resolving (`workflow_driver.py:3054`). **Every route ends in the same place: the operator's response is DROPPED, not refused.**

---

## §2 Coverage-matrix disposition

**No deferred coverage-matrix row is added**, and the absence is a decision, on v2.47 §2's own reasoning: the amended surface has an assigned owner (U-CP-64), and a deferred row alongside an assignment double-books it. No new resolver, no new classification rule and no new property is introduced by CP spec v1.113 — the source column of an owned surface widens.

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Implementation_Plan_Control_Plane_v2_48.md` |
| Version | v2.48 (delta over v2.47) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_47.md` |
| Absorbs | `Spec_Control_Plane_v1_113.md` §1 |
| Trigger | Register row `B-100`, disposition **(a)** pre-selected at its `close_out`; surfaced at the `B-69` impl leg (PR #1166), reported not absorbed |
| Unit-count change | None — ONE amended unit (U-CP-64), zero new units |
| Cluster-count change | None |
| DAG topology change | **None** — within CP or cross-axis; the U-RT-148 → U-CP-64 edge already exists (declared at v2.47 §0.4) |
| Cross-axis cascade | **No new crossing point, no new consumer, no new edge** — the already-crossing structured sequence gains two source-shape members. CXA v2.23 **UNCHANGED**, aggregate frozen at 111 |
| Acceptance-criteria change | ONE ADDED (#A11); #A1 … #A10 **PRESERVED VERBATIM** |
| Carrier / hash impact | **NONE** — read-side only; `B-100` disposition (b) deliberately NOT applied |
| Co-published (this arc) | `Spec_Control_Plane_v1_113.md`; `Spec_Harness_Runtime_v1.md` v1.109; `Implementation_Plan_Harness_Runtime_v2_57.md`; four clearance markers; the `B-100` register row + its prose home **NARROWED to the impl remainder (NOT closed)**; workspace `CLAUDE.md` §2.3 / §2.4 pointer bumps |
| Impl leg | **NOT bundled** — code + tests land as a separate follow-on arc |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.113 into ONE existing unit amendment; fidelity-pure; NO contract addition beyond the spec; NO unit re-decomposition; NO blanket zero-cascade claim |
| Date | 2026-07-31 |
