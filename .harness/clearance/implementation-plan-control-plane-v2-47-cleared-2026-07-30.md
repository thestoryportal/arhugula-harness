---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_47.md
version: v2.47
cleared_at: 2026-07-30T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/council-b69-pause-state-accessor-2026-07-30.md
  - .harness/council-b69-pause-state-accessor-2026-07-30.md §9 row 7 (amend the owning unit; a deferred coverage-matrix row is the WRONG instrument here) + §6.6 (one-authority criterion)
  - .harness/forward-register.yaml row B-69
merge_commit: <pending — this PR>
reviewer_chain:
  - council voices C10 + C11 (both reached the one-authority argument independently; C10 supplied the checkable acceptance criterion)
  - harness-adversarial-reviewer in-family pass
  - out-of-family `just codex-review-uncommitted` (GPT-5.6) — whose [P2] on the "set-returning" shape and [P1] on the never-keyable pre-dispatch identity are what produced §2's return shape and the four-variant union
  - operator AskUserQuestion ratification 2026-07-30 — OPTION A′
  - spec-writer apply pass (this arc)
---

# Clearance — `Implementation_Plan_Control_Plane_v2_47.md`

v2.47 absorbs CP spec **v1.111 → v1.112** into **ONE EXISTING unit amendment — U-CP-64**, the `ResumeContext` carrier-owning unit (per its own v2.21 landing precedent and its v2.42 `hitl_responses` amendment). ZERO new units; ZERO new cluster; ZERO DAG topology change within CP.

**The instrument choice, recorded because it is the council's own finding.** A deferred coverage-matrix row — used correctly at v2.43 / v2.44 / v2.46 for new properties constraining resolvers that do not yet exist — is the **wrong** instrument here, because **this surface has an owner**. §1's provenance carrier amends the same `ResumeContext` U-CP-64 already owns; §2's projection publishes exactly the four resolution channels that carrier is keyed by (`hitl_responses` / `effect_fence_resolutions` / the uniform fallback / non-membership). The two private tree-walks §2 publishes over have no named unit of their own, and v2.44/v2.45 correctly route them to an impl-leg scope-discovery pass — but that disposition is for a *resolver*, not for a public surface whose job is to expose an owned carrier's addressing space.

**Ten added acceptance criteria.** The load-bearing ones: **AC #A2** — non-downgradability asserted by **detect-then-refuse**, not by absence-of-helper (without it, the two-variant carrier *is* the escape value the Runtime-side precondition forbids); **AC #A4** — the `uniform-fallback-only` and `transitively-paused` variants carry **NO identity value of any kind — absent, not opaque, not redacted**, because the pre-dispatch internal identity is a `run_id`-shaped string an operator would key, hitting the resolver's collision defence and having the response **silently DROPPED rather than refused — livelock with no diagnostic**; **AC #A5** — TOTAL enumeration over gate-owning locations, because omitting a pre-dispatch location **inverts** the downstream operator's safety judgment; **AC #A6** — bare identifier sets REFUSED as the return shape; **AC #A7** — the checkable one-authority criterion carried **verbatim** and duplicated at Runtime plan v2.55 AC #9; **AC #A8** — a drift witness asserting the projection and the uniform-fallback resolvers agree on gate-ownership for the same tree.

**Cross-axis cascade is named, not assumed away.** U-RT-148 consumes §2's projection and fences on §1's carrier. **No NEW crossing point** — the same boundary three sibling public CP computations already use — **but the payload widens materially, from three scalars to a structured sequence.** This is stated explicitly rather than as a blanket zero-cascade claim, which is the mistake v2.46's own first draft made and had corrected pre-merge.

**Caveats for Phase 7 consumers.** Spec + impl do NOT land together. This delta amends **no** topology unit (U-CP-86 / U-CP-88 / U-CP-89) — §2 publishes a read over an existing tree and changes no dispatch site; that is stated explicitly because v2.42's own round-1 draft amended exactly those three units on an empirically false call-graph claim. All prior U-CP-64 acceptance criteria are PRESERVED VERBATIM. The `Spec_Control_Plane_v1_106.md` §3 follow-on **(b)** is UNTOUCHED by this arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- One design note is carried for the impl leg, not as a contract term: §1's carrier and §2's projection are discriminated-variant problems on the same two objects — author the discrimination once, or three ad-hoc shapes will ship.
- See `.harness/clearance/README.md` for marker discipline.
