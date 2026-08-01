# Implementation Plan: Harness Runtime — v2.57 (delta over v2.56)

*v2.57 is the Runtime plan leg of register row **`B-100`**'s spec leg, absorbing **Runtime spec v1.108 → v1.109** (ONE amendment site inside §14.14.9.2: the key-ABSENT treatment generalized from a **PROVENANCE** scope to a **STATE** scope, adding a KEY-ABSENT sibling SOURCE SHAPE for the LINEAR and orchestrator carriers). **ONE EXISTING unit is amended — U-RT-148**, the DTO-owning unit; its §1 scope statement's source-shape enumeration and its **AC #15(b)** + **AC #16(a)** are widened from the single crash-reconstruction shape to all three effect-fence carriers' key-absent shapes. **ZERO new units; ZERO new cluster; ZERO DAG topology change — the U-RT-148 → U-CP-64 edge already exists and no new one is added.** The VARIANT set is unchanged at FOUR, so no new DTO variant, no new cause member, no new emission and no new posture arises. This is the SPEC LEG's plan absorption only — impl (code + tests) is a separate follow-on arc per the `B-33` / `B-39` / `B-59` / `B-69` / `B-70` / `B-72` / `B-97` precedent.*

**Status:** Proposed

---

## §0 Change-note (v2.56 → v2.57)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_56.md` (v2.56 — the RATIFIED `B-97` half (a) arc's Runtime plan leg; ONE new unit (U-RT-149), zero existing units amended).

### §0.2 Revision context

Runtime spec v1.109 §14.14.9.2 generalizes the key-ABSENT rule: **any effect-fence source shape whose captured `idempotency_key` is EMPTY carries NO key field**. `EffectFenceAddressable` therefore spans **SIX** source shapes (was FOUR) and the union spans **TEN** (was EIGHT), across an **UNCHANGED SEVEN** distinct source carriers — **THREE** of which now yield two shapes each (the branch, orchestrator and LINEAR effect-fence carriers), so 4 single-shape + 3 dual-shape carriers = 7 carriers spanning 10 shapes. **The four DTO variants are UNCHANGED.** CP's parallel publication is at `Spec_Control_Plane_v1_113.md` §1, absorbed at `Implementation_Plan_Control_Plane_v2_48.md` §1 (AC #A11).

### §0.3 Why U-RT-148 must be amended rather than left to inherit the spec

`[HIGH]` U-RT-148 is the unit that materializes the §14.14.9.2 DTO, and **two of its acceptance criteria name the crash-reconstruction shape specifically** rather than the general rule:

- **AC #15(b)** requires that *"the empty-`idempotency_key` crash-reconstruction source shape cannot be constructed carrying a key at all"* and, symmetrically, that *"a normal branch/orchestrator source shape cannot be constructed WITHOUT one."* Under v1.109 the second clause is **now false as written for the LINEAR and orchestrator carriers**: a key-bearing shape of either still must not be constructible without a key, but a *key-absent sibling of the same carrier* must be — and AC #15(b)'s current phrasing would refuse it.
- **AC #16(a)** exercises only the crash-reconstruction carrier.
- The unit's **§1 scope statement** carries the pre-v1.109 counts (*"SEVEN source shapes"*, *"present on exactly three of the seven"*, *"`EffectFenceAddressable` (3 shapes)"*), which v1.109's recount supersedes.

**Left unamended, an impl leg building to U-RT-148 would ship a DTO that satisfies every criterion and still violates v1.109 §14.14.9.2** — the criteria would actively refuse the two new shapes. That is the reason this delta exists; it is not bookkeeping.

### §0.4 Cross-axis cascade — NONE NEW, determined rather than assumed

U-RT-148 already **depends on** U-CP-64, declared at v2.55 and re-stated at `Implementation_Plan_Control_Plane_v2_47.md` §0.4. This delta adds **no new edge, no new crossing point, and no new consumer** — the already-crossing structured sequence gains two source-shape members, and U-RT-148 consumes it at the same boundary. **CXA determination: `Cross_Axis_Composition_Document_v2_23.md` is UNCHANGED, aggregate FROZEN at 111.** OD, IS and AS specs and plans are **UNCHANGED** — §14.14.9.5's trace-emission row requires **per-variant counts, one per classification: FOUR**, and the variant set is unchanged, so the OD-owned `§C-OD-30.5` attribute schema is untouched. *(Determined by reading the emission row, not assumed from "read-side only".)*

### §0.5 What this delta does NOT do

- It does **NOT** add a unit, a cluster, or a DAG edge.
- It does **NOT** amend U-RT-149 (the `B-97`(a) keying / migration / `harness-inspect` unit), U-RT-148's AC #1 – #14, or any §30 / §14.14.8 / §13.7 obligation. All are **PRESERVED VERBATIM**.
- It does **NOT** add a DTO variant, a cause member, an emission, or a posture. **Sixteen acceptance criteria remain sixteen** — two are widened in scope, none is added or removed.
- It does **NOT** add a capture-side obligation. `B-100` disposition **(b)** is NOT applied; no carrier gains a length constraint and `snapshot_hash` is untouched.
- It does **NOT** close the SCALAR uniform-fallback channel, **REGISTERED as `B-107`**. The widened AC #15(b) / #16(a) constrain the **DTO**; they cannot constrain `resume_context.effect_fence_resolution`, a scalar the caller sets independently, and `compute_effect_fence_uniform_fallback_eligible_key` (`workflow_driver.py:2935`–`:2970`) does not filter empty keys. **Do NOT read these criteria green as evidence that channel is closed.**

---

## §1 U-RT-148 amendment — the KEY-ABSENT sibling source shapes

**Unit ID:** U-RT-148 (EXISTING — amended, not re-decomposed)
**Spec anchors:** `Spec_Harness_Runtime_v1.md` v1.109 §14.14.9.2; consumes `Spec_Control_Plane_v1_113.md` §1
**Prior scope preserved:** every U-RT-148 obligation at v2.55 except the three sites named at §0.3. **AC #1 – #14 are PRESERVED VERBATIM.**

### §1.1 Amended scope statement — the source-shape enumeration

The unit's §1 scope item 2 is amended in its **counts and enumeration only**; every other clause (the closed four-variant union, the root-level `workflow_id` / `created_at` / staleness token, `pause_reason` over the SIX-member domain, `step_index` on every projection, declared closed domains rather than inherited `str`, per-source-shape rather than per-variant field carriage, impl-discretion of spelling with unrepresentability as the contract term) is **PRESERVED VERBATIM**. The corrected enumeration:

**SHAPE ≠ CARRIER.** There are **SEVEN** distinct source carriers; the union discriminates by **SHAPE**, and three carriers each yield **two** shapes — key-bearing and key-absent — for **TEN** source shapes in total. `EffectFenceAddressable` spans **SIX** of them:

| Variant | Source shape | `step_kind` | Key field |
|---|---|---|---|
| `HitlAddressable` | `PausedChildBranchResumeState` | absent | child `run_id` |
| `EffectFenceAddressable` | `EffectFencePausedBranchResumeState` | present | `idempotency_key` |
| `EffectFenceAddressable` | `EffectFencePausedBranchResumeState`, **captured key EMPTY** | present | **absent** |
| `EffectFenceAddressable` | `OrchestratorEffectFencePausedResumeState` | present | `idempotency_key` |
| `EffectFenceAddressable` | `OrchestratorEffectFencePausedResumeState`, **captured key EMPTY** | present | **absent** |
| `EffectFenceAddressable` | LINEAR `EffectFenceResumeState` | absent | `idempotency_key` |
| `EffectFenceAddressable` | LINEAR `EffectFenceResumeState`, **captured key EMPTY** | absent | **absent** |
| `UniformFallbackOnly` | `PreDispatchGateOwningBranchResumeState` | present | **absent** |
| `UniformFallbackOnly` | depth-0 ROOT gate-owning pause | absent | **absent** |
| `TransitivelyPaused` | container node | absent | **absent** |

`step_kind` is present on **FIVE** shapes and absent from **FIVE**. **No `step_kind` capture is added anywhere** — each key-absent shape inherits its carrier's existing field set exactly, minus the key. The **SOURCE-SHAPE SUB-DISCRIMINATOR** is therefore required for `EffectFenceAddressable` (**6 shapes**) and `UniformFallbackOnly` (**2 shapes**), and unnecessary for `HitlAddressable` and `TransitivelyPaused` (1 each). **The discriminator keys on the source SHAPE — a tag the projection stamps — not on any field of the source carrier, which is why the two new shapes need no new machinery.**

### §1.2 Amended AC #15(b) — the KEY field, over ALL THREE effect-fence carriers

**AC #15(a) is PRESERVED VERBATIM.** AC #15(b) is widened from the crash-reconstruction shape to the general rule, retaining its detect-then-refuse posture and both its directions:

> **AC #15(b) — the KEY field, the harder half, and the one a single optional-field model would silently pass.** For **each** of the three effect-fence carriers (`EffectFencePausedBranchResumeState`, `OrchestratorEffectFencePausedResumeState`, the LINEAR `EffectFenceResumeState`): assert that its **KEY-ABSENT source shape cannot be constructed carrying a key at all**, AND — symmetrically — that its **KEY-BEARING source shape cannot be constructed without one, nor carrying an EMPTY one**. **Assert the refusals, not merely that the happy paths work.**

*The empty-string direction is what the widening adds and is the load-bearing half: a key-bearing shape that accepts `""` reintroduces exactly the value v1.109 §14.14.9.2 exists to keep off the boundary, while passing an absence-only assertion. Without the per-carrier quantifier, an implementation using one `EffectFenceAddressable` model with an optional key satisfies the criterion by omitting the key for crash reconstruction while still permitting a LINEAR projection with a `""` key — an illegal state, and representable (the round-12 [P1] defect class, one carrier over).*

### §1.3 Amended AC #16(a) — the empty-fence-key state, over ALL THREE carriers

**AC #16(b) (the SCALAR-field staleness binding) is PRESERVED VERBATIM.** AC #16(a) is widened:

> **AC #16(a) — the empty-fence-key state.** Construct **(i)** a fan-out **crash-reconstruction** pause, **(ii)** a **LINEAR** effect-fence pause, and **(iii)** an **ORCHESTRATOR** effect-fence pause, each whose fence carrier holds an **EMPTY `idempotency_key`**, and assert each projects as `EffectFenceAddressable` **with the key field ABSENT** — its own source shape, **never** carrying a `""` key value, and never omitted from the enumeration.

**Witness-shape constraints, stated so a later closeout does not demand an unbuildable witness.** `[HIGH]`

- **(iii) MUST be a CONSTRUCTED-SNAPSHOT test, never an end-to-end run.** The orchestrator carrier's sole shipped capture site (`harness-cp/src/harness_cp/workflow_driver.py:12392`) guards on a **truthy** key at `:12376`–`:12381`, so **no production path can produce this state**. The shape is declared on TYPE-TOTALITY grounds — the carrier type admits `""` (`idempotency_key: str`, no length constraint) and the projection is a total function over journaled records that outlive the capture-site code that wrote them. *Register row `B-100` asserted the opposite of that guard's presence; the premise was checked at the spec leg and found FALSE (`Spec_Harness_Runtime_v1.md` v1.109 change-note finding (i)). The disposition is unchanged; only its ground is.*
- **(ii) is genuinely reachable** — the LINEAR capture site constructs its carrier whenever the runtime error's `idempotency_key` attribute `isinstance(_, str)` (`workflow_driver.py:5456`), which admits `""` — so it MUST NOT be downgraded to (iii)'s posture.
- **(i) re-runs the existing v2.55 witness unmodified**; it is now a special case of the general rule, not a separate rule.

**The mechanism the criterion protects differs by site — do not assume the single one `B-100` names.** At the **fan-out per-branch** dispatch sites **and at the ORCHESTRATOR consult** (`workflow_driver.py:12118`) the consult is **gated on a truthy key**, so an empty key is never consulted at all. At the **LINEAR** consult ALONE (`workflow_driver.py:4925`–`:4936`) the resolution IS looked up, but the directive is applied only when the runtime's **recomputed** per-`(run, step, tool)` dispatch key equals it (`harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:1042`, against the key composed at `:989`) — never `""` — so it is threaded and then discarded, and the dispatch re-pauses INERT. And `compute_effect_fence_tree_wide_abort_present` filters all empty keys before resolving (`workflow_driver.py:3054`). **Every route ends in the same place: the operator's response is DROPPED, not refused.**

### §1.4 Closure criterion — UNCHANGED

U-RT-148's closure criterion and its **SIXTEEN** acceptance criteria are otherwise **PRESERVED VERBATIM**, including AC #9's verbatim one-authority criterion (***"Runtime's accessor contains no recursion over `PauseSnapshot` and reads no nested resume-carrier field"***) and AC #13's success/failure emission split. **Two criteria are widened in scope; none is added, removed, or renumbered.**

---

## §2 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Implementation_Plan_Harness_Runtime_v2_57.md` |
| Version | v2.57 (delta over v2.56) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_56.md` |
| Absorbs | `Spec_Harness_Runtime_v1.md` v1.109 §14.14.9.2 |
| Trigger | Register row `B-100`, disposition **(a)** pre-selected at its `close_out`; surfaced at the `B-69` impl leg (PR #1166), reported not absorbed |
| Unit-count change | None — ONE amended unit (U-RT-148), zero new units |
| Cluster-count change | None |
| DAG topology change | **None** — the U-RT-148 → U-CP-64 edge already exists (v2.55; `Implementation_Plan_Control_Plane_v2_47.md` §0.4) |
| Cross-axis cascade | **No new crossing point, no new consumer, no new edge.** CXA v2.23 **UNCHANGED**, aggregate frozen at 111; OD / IS / AS **UNCHANGED** (§14.14.9.5's per-variant counts stay at FOUR) |
| Acceptance-criteria change | **SIXTEEN → SIXTEEN.** #15(b) and #16(a) widened in scope; #1 – #14, #15(a), #16(b) **PRESERVED VERBATIM** |
| Carrier / hash impact | **NONE** — read-side only; `B-100` disposition (b) deliberately NOT applied |
| Co-published (this arc) | `Spec_Control_Plane_v1_113.md`; `Spec_Harness_Runtime_v1.md` v1.109; `Implementation_Plan_Control_Plane_v2_48.md`; four clearance markers; the `B-100` register row + its prose home **NARROWED to the impl remainder (NOT closed)**; workspace `CLAUDE.md` §2.3 / §2.4 pointer bumps |
| Impl leg | **NOT bundled** — code + tests land as a separate follow-on arc |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream Runtime spec v1.109 into ONE existing unit amendment; fidelity-pure; NO contract addition beyond the spec; NO unit re-decomposition; NO blanket zero-cascade claim |
| Date | 2026-07-31 |
