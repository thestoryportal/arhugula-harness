# Implementation Plan: Control Plane — v2.47 (delta over v2.46)

*v2.47 is the CP plan leg of the RATIFIED **B-69 durable-pause-state read accessor arc**'s **spec leg** (council record `.harness/council-b69-pause-state-accessor-2026-07-30.md`; **operator ratified OPTION A′ — CO-REQUISITE, SEQUENCED — 2026-07-30**), absorbing **CP spec v1.111 → v1.112** (§1 the REQUIRED `ResumeContext` response-provenance carrier, non-downgradable; §2 the NEW public projection-returning surface over the two private resume-tree walks; §3 two registered scope-limit lifts). **ONE EXISTING unit is amended — U-CP-64**, the `ResumeContext` carrier-owning unit per its own v2.21 landing precedent and its v2.42 `hitl_responses` amendment. **A deferred coverage-matrix row is deliberately NOT the instrument here** — unlike v2.43 / v2.44 / v2.46, whose new properties constrained resolvers that do not yet exist, **this surface has an owner**. ZERO new units; ZERO new cluster; ZERO DAG topology change **WITHIN CP** — but the arc adds **ONE cross-axis edge, U-RT-148 → U-CP-64**, stated here rather than absorbed into a blanket "zero" *(corrected at out-of-family review round 3 [P2], which caught the same contradiction in the sibling Runtime plan header)*. This is the SPEC LEG's plan absorption only — impl (code + tests) is a separate follow-on arc per the B-33/B-39/B-59/B-70/B-72 precedent.*

**Status:** Proposed

---

## §0 Change-note (v2.46 → v2.47)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_46.md` (v2.46 — the co-designed `B-79`/`B-80` spec leg's CP plan leg; TWO deferred coverage-matrix rows, zero units amended).

### §0.2 Revision context

CP spec v1.112 states two CP-owned surfaces for the B-69 arc:

- **§1 — the `ResumeContext` response-provenance carrier.** A closed two-variant discrimination (accessor-derived, carrying the staleness token **non-optionally**; legacy, carrying none and semantically byte-identical to today), with the legacy variant **not constructible from** an accessor-derived one. The token is opaque to CP; its required PROPERTY and impl-discretion composition are Runtime-owned at `Spec_Harness_Runtime_v1.md` v1.107 §30.
- **§2 — the public projection-returning surface.** One function returning an ordered sequence of typed location projections carrying the **authoritative FOUR-variant classification** plus tree position, spanning **seven-plus source shapes** — including the empty-`idempotency_key` crash-reconstruction source shape of `effect-fence-addressable`, whose **key field is ABSENT** (a draft made it a fifth VARIANT; out-of-family review round 11 [P1] showed that would break one-authority, since the empty-key distinction is not derivable from properties 1-8) — publishing what the private resume-tree walks compute, so Runtime's accessor never re-derives a safety classification.

### §0.3 Why U-CP-64, and why an amendment rather than a deferred row

**U-CP-64 is the `ResumeContext` carrier-owning unit.** It carried `hitl_responses` / `hitl_response_for` at v2.42 (the B-39 arc) on the strength of its own v2.21 authoring of that carrier. **§1 amends the same carrier**, so the owner is unambiguous.

**§2's ownership is the question worth stating rather than assuming.** The two private tree-walks it publishes over have never been assigned to a named unit — v2.44 / v2.45 route them into an impl-leg **scope-discovery** pass rather than to an owner. That is correct for a *resolver that does not yet exist*; it is **wrong for a public surface whose entire job is to expose the classification U-CP-64's own carrier is keyed by**. The projection's four variants are exactly the four resolution channels of `hitl_responses` / `effect_fence_resolutions` / the uniform fallback / non-membership — the carrier's own addressing space, published. **⇒ U-CP-64 owns both, and a deferred coverage row would strand a surface that has an owner** (the instrument-selection error the council named explicitly).

### §0.4 Cross-axis cascade — real, and named rather than assumed away

`harness-runtime`'s NEW U-RT-148 accessor (`Implementation_Plan_Harness_Runtime_v2_55.md`) consumes §2's projection surface and fences on §1's carrier. **No NEW crossing point is introduced** — the consumption rides the SAME `harness-runtime` → `harness-cp` boundary that **three sibling public CP computations** (the HITL uniform-fallback-eligible run-id computation, the effect-fence uniform-fallback-eligible-key computation, and the effect-fence tree-wide-abort-presence computation) are already consumed across. **But the touch is real and the PAYLOAD widens materially — from three scalars to a structured sequence — and this delta says so rather than repeating v2.46's own corrected mistake of a blanket "zero cross-axis cascade" claim.** CXA determination at `Cross_Axis_Composition_Document_v2_23.md`: **no new §2.3 row, aggregate frozen at 111**, with the payload widening recorded.

**Dependency edge:** U-RT-148 **depends on** U-CP-64 (as amended here).

### §0.5 What this delta does NOT do

- It does **NOT** amend U-CP-86 / U-CP-88 / U-CP-89 (the topology units) — §2 publishes a read over an existing tree; it changes no dispatch site. *(Stated explicitly because v2.42's own round-1 draft amended exactly those three units on an empirically false call-graph claim; that error is not repeated by assumption here.)*
- It does **NOT** amend any unit owning §1.2 properties 1–5 or §1.1 properties 6–8. Those are **PRESERVED VERBATIM** at the spec; §2 publishes their classification and defines none of it.
- It does **NOT** open the `(workflow_id, run_id)` multi-run-disambiguation extension.
- It adds **NO** new unit, **NO** new cluster, and **NO WITHIN-CP DAG topology change**. *(Qualified at out-of-family review round 6 [P2]: a blanket "no DAG topology change" here contradicted §0.4's own new cross-axis edge and would have handed a scheduler two different graph definitions.)* **The arc DOES add cross-axis edges into U-CP-64** — from `Implementation_Plan_Harness_Runtime_v2_55.md`'s U-RT-148, which consumes §2's projection and fences on §1's carrier. Those edges are declared on the Runtime side, where the dependent unit lives; **no CP unit gains a dependency**, which is what "no within-CP topology change" means and all it means.

---

## §1 U-CP-64 amendment — `ResumeContext` response-provenance carrier + the public projection-returning surface

**Unit ID:** U-CP-64 (EXISTING — amended, not re-decomposed)
**Spec anchors:** `Spec_Control_Plane_v1_112.md` §1 + §2 + §3; consumed cross-axis by `Spec_Harness_Runtime_v1.md` v1.107 §31 (C-RT-36)
**Prior amendments preserved:** v2.21 (original `ResumeContext` authoring), v2.42 (`hitl_responses` / `hitl_response_for` keyed by the paused child's own `run_id`; the `DriverContext.resume_context_holder` CONTRACT-level retirement). **All prior U-CP-64 acceptance criteria are PRESERVED VERBATIM**; the criteria below are ADDED.

### §1.1 Added scope

**(a) The §1 provenance carrier** — the closed two-variant discrimination on `ResumeContext`, with the token non-optional on the accessor-derived variant, absent on the legacy variant, and no construction path from the former to the latter (frozen carriers, consistent with `PauseSnapshot`).

**(b) The §2 projection-returning surface** — one public function returning an **ordered sequence** of typed location projections over the resume tree of a supplied pause snapshot, carrying per location: the authoritative variant (HITL-addressable with the child's own `run_id` / effect-fence-addressable with `idempotency_key` / uniform-fallback-only with **NO key field** / transitively-paused with **NO key field**) — with the empty-`idempotency_key` crash-reconstruction carrier modelled as a FOURTH effect-fence-addressable **SOURCE SHAPE whose key field is ABSENT**, never as a `""` key value both resume sites ignore (which would drop the operator's response silently rather than refuse it); `pause_reason` from the **SIX**-member domain including `EFFECT_FENCE_AMBIGUOUS`; `step_index`; and `step_id` / `branch_index` / `step_kind` **where the source carrier declares them** — `step_kind` present on three source carriers and **absent from `PausedChildBranchResumeState`**, so each variant declares the fields its own carrier actually has, with **declared closed domains rather than inherited `str`**.

**(c) The §3 lifts, reflected in the unit's own scope notes** — the `resume_handle` addressing limitation lifts **only for a caller who takes the read**, **only in conjunction with the Runtime-side precondition**, and **only for ADDRESSING** — §1.1(a)'s 2+-member INERT re-pause safety rule is PRESERVED VERBATIM and is not relaxed.

### §1.2 Added acceptance criteria

**AC #A1 — the carrier is REQUIRED, and read-then-omitted is unrepresentable.** Assert by test that there is no way to hold an accessor read and construct a token-free accessor-derived `ResumeContext`. *An optional token would make omission itself the prohibited escape: `resume()` cannot distinguish "read, then omitted" from "never read", leaving every accessor user's default path unfenced — safe-by-diligence, which is a species of luck.*

**AC #A2 — non-downgradability, by DETECT-THEN-REFUSE.** Assert that no construction path yields a legacy variant **from** an accessor-derived one — no downgrade helper, no `.without_token()`, no field mutation. **Assert the refusal, not merely the absence of a helper.** *This constraint is what keeps the Runtime-side no-escape-value rule intact: without it the two-variant carrier IS the escape value the precondition forbids.*

**AC #A3 — legacy byte-compatibility.** Assert an existing caller constructing the legacy variant observes behavior **byte-identical to pre-v1.112** — every existing `hitl_response` / `hitl_responses` / `effect_fence_resolution` / `effect_fence_resolutions` semantic unchanged.

**AC #A4 — the FOUR variants, the SOURCE SHAPES, and the ABSENT key fields.** Assert the projection returns all four variants against a tree containing one of each, assert that a fan-out crash-reconstruction carrier holding an **EMPTY `idempotency_key`** projects as effect-fence-addressable **with the key field ABSENT** (never carrying `""`), and — **the load-bearing assertion** — that the `uniform-fallback-only` and `transitively-paused` variants carry **NO identity value of any kind**: not opaque, not redacted, **ABSENT** — and the same for the empty-`idempotency_key` source shape, whose `""` must never be surfaced as a key field. *The pre-dispatch internal identity is a `run_id`-shaped string; an operator who keys it hits the resolver's collision defence, which counts that response as unaddressed — **the response is silently DROPPED, not refused. Livelock with no diagnostic.** Absence makes the v1.108 §1.1(b) prohibition a type invariant rather than a convention.*

**AC #A5 — TOTAL enumeration over gate-owning locations, across BOTH `uniform-fallback-only` source shapes.** (a) Construct a tree containing a **pre-dispatch** gate-owning location alongside an addressable one; assert **BOTH** appear. (b) Construct a **depth-0 root gate-owning pause** (a top-level LINEAR / `EVALUATOR_OPTIMIZER` / `DECENTRALIZED_HANDOFF` HITL pause with no fan-out carrier); assert it appears as **`uniform-fallback-only`**, **not** `HITL-addressable` and **not** omitted. *Property 4's sole-member rule fires at exactly 1 — omit either and the downstream operator's safety judgment **inverts**; render (b) as addressable and the operator gets a map key the resolver **silently ignores rather than refuses**.* **(b) was absent from this delta's first draft and was caught by out-of-family review round 1 [P1]; the shipped resolver was read directly to confirm the shape before the union's source column was widened — the variant SET stayed at four because the semantics were already right.**

**AC #A6 — bare identifier sets are REFUSED as the return shape.** Assert the surface returns structured projections, not `list[str]` / `set[str]`. *A bare set cannot populate position, step, reason and addressability without the caller re-walking — the very thing this surface prevents — and it is worse than insufficient: it would carry the one value that must not cross the boundary (AC #A4).*

**AC #A7 — the one-authority criterion, CHECKABLE and carried VERBATIM.** ***Runtime's accessor contains no recursion over `PauseSnapshot` and reads no nested resume-carrier field.*** *(Carried verbatim from `Spec_Control_Plane_v1_112.md` §2.3 and duplicated at `Implementation_Plan_Harness_Runtime_v2_55.md` AC #9, so neither side can drift from it unilaterally. "Must not re-walk" as prose is not verifiable; this is.)*

**AC #A8 — ONE SHARED TRAVERSAL, not merely agreeing outputs.** `[HIGH]` **The resolvers and the projection MUST consume a single shared traversal of the resume tree** — the projection is a view over the walk the resolvers already use, not a second walker whose results happen to match. *(Strengthened at out-of-family review round 16 [P1]: `_collect_gate_owning_run_ids` and `_collect_effect_fence_idempotency_keys` are already separate recursive walks, so an output-agreement-only criterion would let a THIRD classification authority ship and pass on every finite tested tree — recreating exactly the drift this contract exists to eliminate, just later and harder to find.)* **Assert structurally** that no independent recursion over `PauseSnapshot` is introduced for the projection, **in addition to** asserting the projection surface and the uniform-fallback resolvers agree on gate-ownership for the same tree — i.e. every location the resolvers count as gate-owning appears in the projection with a gate-owning variant, and no location the resolvers treat as a traversable container appears as addressable. *The concrete harms this forecloses: listing a container as addressable invites the operator to key a response the resolver will refuse (livelock); omitting a gate-owning branch the resolver counts leaves it unaddressed (misattribution — the exact property-4 harm). These semantics were corrected three times in six weeks; a second authority would already have had three chances to diverge.*

**AC #A9 — properties 1–8 unchanged.** Re-run the existing property-1-through-8 witnesses green, unmodified. *§2 publishes the classification; it defines none of it.*

**AC #A10 — the shape constraint.** Assert the projection is not shaped to imply the pause journal *is* the HITL approval queue — no TTL field, no per-item status field, no queue-lifecycle vocabulary. *The two surfaces have deliberately different postures, and conflating them in a type is how that difference gets lost.*

### §1.3 One convergence carried forward for the impl leg

§1's carrier and §2's projection are **discriminated-variant problems on the same two objects**. **Author the discrimination ONCE, in one idiom** — or three ad-hoc shapes will ship (the carrier's two-variant split, the projection's four-variant union, and Runtime's DTO). This is a design note for the impl leg, not an additional contract term.

---

## §2 Coverage-matrix disposition

**No deferred coverage-matrix row is added at this delta**, and the absence is a decision. v2.43 / v2.44 / v2.46 each used that instrument correctly, for new spec properties constraining **resolvers that do not yet exist**. CP v1.112 §1 and §2 are not that: both are surfaces on an **owned** carrier, assigned above. Adding a deferred row alongside an assignment would double-book the same surface.

**The two §3 lifts likewise add no row** — a lift discharges a registered limitation; it introduces no new coverage obligation. The `Spec_Control_Plane_v1_106.md` §3 follow-on **(b)** — the pre-existing `effect_fence_resolution_for` uniform-fallback gap — is **UNTOUCHED** by this delta (it was separately filed as `B-70` and separately resolved at `Spec_Control_Plane_v1_107.md`).

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Implementation_Plan_Control_Plane_v2_47.md` |
| Version | v2.47 (delta over v2.46) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_46.md` |
| Absorbs | `Spec_Control_Plane_v1_112.md` §1 + §2 + §3 |
| Authoring authority | `.harness/council-b69-pause-state-accessor-2026-07-30.md` §9 row 7; operator ratification 2026-07-30 (OPTION A′) |
| Co-published artifacts (this arc) | `Spec_Control_Plane_v1_112.md`; `Spec_Harness_Runtime_v1.md` v1.107; `Spec_Operational_Discipline_v1_36.md`; `Cross_Axis_Composition_Document_v2_23.md`; `Implementation_Plan_Harness_Runtime_v2_55.md`; six clearance markers; `B-69` register rows; workspace `CLAUDE.md` §2.3/§2.4 pointer bumps |
| Unit-count change | None — ONE amended unit (U-CP-64), zero new units |
| Cluster-count change | None |
| DAG topology change | None within CP; ONE new cross-axis edge U-RT-148 → U-CP-64 |
| Cross-axis cascade | **Real and named** — U-RT-148 consumes §2's projection and fences on §1's carrier; **no NEW crossing point** (same boundary three sibling public CP computations already use) but the **payload widens materially, three scalars → a structured sequence**. CXA v2.23: no new row, aggregate frozen at 111 |
| Impl leg | NOT bundled — code + tests land as a separate follow-on arc, subject to the arc's ordering constraint (**staleness precondition first or simultaneous, never after**) |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.112 into ONE existing unit amendment; fidelity-pure; NO contract addition beyond the spec; NO unit re-decomposition; NO DAG topology change; NO blanket zero-cascade claim |
| Date | 2026-07-30 |
