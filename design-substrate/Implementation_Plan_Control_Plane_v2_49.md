# Implementation Plan: Control Plane — v2.49 (delta over v2.48)

*v2.49 absorbs CP spec v1.115's B-107 A-hybrid amendment. ONE existing unit, U-CP-64, is amended;
no new unit, cluster, DAG node, dependency edge, or CXA row is introduced. AC #A1–#A11 are
preserved verbatim.*

**Status:** Proposed

## §0 Change-note (v2.48 → v2.49)

### §0.1 Owner and scope

U-CP-64 already owns `ResumeContext`, its effect-fence response surfaces, and the §2 projection
surface. Spec v1.115 changes that owned map domain and scalar classification boundary, so amending
U-CP-64 is the only coherent owner; minting a unit would split one response/resolution surface.

### §0.2 Preservation and graph

AC #A1–#A11 are preserved verbatim. No new carrier, capture, hash, Runtime, or cross-axis consumer
is introduced. The U-RT-148 → U-CP-64 edge remains the only existing relevant cross-axis edge;
this plan has no new edge and its dependency graph remains unchanged and acyclic.

## §1 U-CP-64 amendment — B-107 A-hybrid empty-key closure

**Unit ID:** U-CP-64 (existing — amended, not re-decomposed)
**Spec anchors:** `Spec_Control_Plane_v1_115.md` §1.1–§1.5 (amending v1.107 §1.1 and v1.112 §2.1).
**Depends on:** existing U-CP-64 dependencies unchanged.

### §1.1 Added acceptance criterion

**AC #A12 — A-hybrid empty-key resolution closure, with mutation probes.**

1. Exercise the **eight-cell grid**: map and scalar channels at LINEAR, PARALLELIZATION branch,
   ORCHESTRATOR_WORKERS worker, and ORCHESTRATOR-own carrier. Every PARALLELIZATION and
   ORCHESTRATOR_WORKERS case includes an empty-key location alongside a keyed sibling in both
   carrier orders; neither empty-key case may suppress the keyed sibling. Both ORCHESTRATOR-own
   cases are constructed-snapshot tests, not e2e tests. The two ORCHESTRATOR-own cells witness
   construction and classification semantics only — the shipped orchestrator consult is
   truthiness-gated on the captured key, so those cells cannot discriminate the §1.3
   resolver-boundary guard; §1.3 discrimination binds at the LINEAR and branch-scan cells (whose
   consults are ungated), and clause 5's mutation claim is carried there, never by these two cells.
2. Prove scalar membership removal: the uniform-fallback candidate computation excludes `""`, the
   b80 assertion (`test_map_addressed_keyed_abort_activates_alongside_an_unrelated_keyless_pause`'s
   final `is False` assert in `test_workflow_driver_effect_fence_tree_wide_abort_b80.py`; its
   sole-keyless and two-keyed sibling asserts stay `False`) flips to `True`, and a direct caller-supplied
   `effect_fence_uniform_fallback_eligible_key=""` produces no directive.
3. Prove map construction, compatibility, and copy semantics (PD-8): construction with
   `{"": …}` rejects; item assignment through the stored mapping (including
   `context.effect_fence_resolutions[""] = …`) rejects; mutating the caller's original mapping
   cannot change the stored mapping; and a valid pre-amendment map retains byte-identical serialized
   logical content and resolution meaning. The probe fails if validation, copying, immutability, or
   valid-map serialization compatibility is removed.
4. Prove validation-bypassing defence in depth: a `model_construct` context carrying an empty map
   key is inert — no directive is threaded and a keyed sibling's directive survives. This is not a
   diagnostic or closure-criterion assertion.
5. Re-derive and cover every resolver reader under B-107's binding rule: at this revision seven
   resolver call sites and two non-test terminal key-match consumers. The witness set fails if the
   resolver empty-key guard is removed.

## §2 Coverage and remainder

`Spec_Control_Plane_v1_115.md` §1.1–§1.5 is covered by U-CP-64. B-107 remains open until this
implementation, the b80 update, the eight cells, and the PD-8 probes land; B-101 is not merged or
otherwise affected by that fact. B-101 remains separately closed under (b)-PLUS and its promotion
trigger to the closed variant discriminator remains unchanged.

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_49.md` |
| Absorbs | `Spec_Control_Plane_v1_115.md` §1 |
| Unit change | ONE existing unit amended: U-CP-64 |
| Acceptance change | ONE added AC #A12; #A1–#A11 preserved verbatim |
| DAG / CXA | None; existing graph remains acyclic; no new CXA row |
| Impl leg | Separately owed and not bundled |
