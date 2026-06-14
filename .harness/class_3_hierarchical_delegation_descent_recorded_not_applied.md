# Class 3 (informational) — HIERARCHICAL_DELEGATION gate-level descent is recorded-not-applied to the child's executed gate

| Field | Value |
|---|---|
| Class | 3 (informational; non-blocking; documents a design-consistent behavior a reviewer might mistake for a bug). |
| Authority | C-CP-12 §12.2 (sub-agent gate-level descent) + C-RT-59 §14.7.2/§14.7.4 (sub-agent dispatch + child-context sharing). |
| Surfaced at | R-FS-1 arc #15 (U-CP-89 `HIERARCHICAL_DELEGATION`), 2026-06-14. Reused behavior, not introduced by U-CP-89. |
| Tests | `harness-cp/tests/test_workflow_driver_hierarchical_delegation.py::test_sub_agent_descent_is_equality_default_recorded_not_applied` + `…_gate_level_monotonic_across_depth`. |

## Observation

C-CP-12 §12.2 specifies gate-level descent across a sub-agent boundary as **monotonic `≤`, with EQUALITY as the valid default** — NOT strict descent. The `GateLevel` ordering is `AUTO(0) < ASK(1) < DENY(2)`; "descent" means the child's gate level may not be *more permissive* than the parent's, and equality satisfies that.

Two facts compose:

1. **`dispatch_sub_agent` always returns `child_gate_level == parent_gate_level`.** The blast-radius *downgrade* a sub-agent may carry rides `child_blast_radius_ceiling` (the AS-axis sandbox-tier floor, C-AS-02), **not** the CP gate level. So the computed `SubAgentGateLevelDescent` is, at the v1.6 MVP, an equality by construction.

2. **The child re-seeds its executed gate from its own manifest.** `child_workflow_runner` re-enters `execute_workflow` with the child's `WorkflowManifestEntry`; the child's per-step gate evaluation reads `resolve_parent_gate_level(child_manifest)` + the child's own placements. The computed descent value is **recorded** (it travels in the `HandoffContext` / audit surface for traceability) but is **not applied** as an override onto the child's executed gate — the child's executed gate is whatever its own manifest + placements produce.

## Why this is correct (not a defect)

- "Strict descent" was never the contract — §12.2 is `≤` with equality the default, so a child executing at the same gate level as its parent is in-spec.
- The recorded-not-applied split is the faithful realization of "the descent is an audit/traceability fact; the child's executed authority comes from its own manifest." Conflating the two (forcing the parent's descent onto the child's executed gate) would *override* the child manifest's declared gate posture — the opposite of the per-manifest authority the design intends.
- The monotonic invariant the tests assert is therefore: across any depth, no child executes at a *more permissive* gate than its parent's recorded floor — which holds because equality is the default and the child re-seeds from its own (admissible) manifest.

## Scope note

This note documents the **CP-strategy + sub-agent-dispatch gate semantic**. It is independent of (and must not be conflated with) the runtime sync/async-bridge deadlock recorded at `runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md` — that defect blocks the *real-provider* sub-agent INFERENCE path end-to-end; this note is about the *gate-level* contract, which the CP unit suite exercises with a faithful dispatcher double regardless of the runtime bridge.
