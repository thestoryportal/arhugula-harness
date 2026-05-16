# Class 1 Tension — `RoleRoutingBinding` / `WorkloadRoutingOverride` underspecified

**Status:** 🛑 Class 1 — OPEN. Two `RoutingManifest` sub-records cannot be specified without inventing a field set.
**Filed:** 2026-05-16 (Phase 7 7b, CP axis-stream — during the v2.9 plan revision pass).
**Scope:** `RoleRoutingBinding`, `WorkloadRoutingOverride` — constituent value-types of U-CP-04's `RoutingManifest`.

## Root cause

U-CP-04's `RoutingManifest` (v2.1 plan body) declares:

```
per_role_bindings      : Map<AgentRole, RoleRoutingBinding>
per_workload_overrides : Map<WorkloadClass, WorkloadRoutingOverride>
```

`RoleRoutingBinding` and `WorkloadRoutingOverride` are consumed at these signature
positions with **no field set declared anywhere in the plan or the spec**.

## Why this is Class 1 (NOT a v2.9 factor-out)

The CP plan v2.9 revision pass specified the Pattern-D *tail* structured types as
faithful factor-outs of the operator-ratified T2 X-AL-3 resolution
(`.harness/xal3_resolution_recommendations.md`). These two records are **NOT**
covered by that ratification:

- **Not in T2.** The T2 resolution table has no verdict row for `RoleRoutingBinding`
  or `WorkloadRoutingOverride`. The T1 shared-type carrier map only *proposed* them;
  T2 did not pick them up. Extending the FACTOR-OUT ratification to them by analogy
  would be an unauthorized X-AL-3 extension.
- **No committing contract decomposes them.** `C-CP-06 §6.1` `WorkflowManifestEntry`
  enumerates `workflow_class`, `engine_class`, `f3_invocation_default`,
  `routing_layer_budgets`, `fallback_chain`, `topology`, `hitl_placements` — it does
  **not** declare a `per_role_bindings` / `per_workload_overrides` sub-record.
  `C-CP-01 §1.3` gives the manifest authoring grain "per agent role × per workflow
  class × per step" **in prose only** — it enumerates no `RoleRoutingBinding` /
  `WorkloadRoutingOverride` field set. The two records originate in the v2.1 U-CP-04
  plan body — they are plan-side, not spec-committed.

Inventing a field set for either record would be an X-AL-3 design extension
(`CLAUDE.md` I-2). No field set was invented — per `implementation-planner`
SKILL.md §2: surface the gap, do not invent the trace.

## Impact — U-CP-04 `RoutingManifest` partial-land

CP plan v2.9 §0.5 + §2A-U-CP-04 acceptance criterion 5: `RoutingManifest`
**partial-lands**.

- ✅ Materializes: `manifest_version`, `fallback_chains`, `retry_policies`
  (`RetryPolicy` itself is a v2.9 T2 factor-out — C-CP-03 §3.5 — and lands).
- 🛑 Blocked: `per_role_bindings` and `per_workload_overrides` — their `Map`
  value-types (`RoleRoutingBinding` / `WorkloadRoutingOverride`) land with a
  deferred opaque placeholder value-type pending resolution of this record.

## Routing

Class 1. Two resolution paths, operator decides:

1. **Spec revision** — `Spec_Control_Plane_v1_3.md` C-CP-01 §1.3 (or C-CP-06 §6.1)
   amended to commit a concrete `RoleRoutingBinding` / `WorkloadRoutingOverride`
   field schema; CP plan then absorbs it as a faithful factor-out (revision pass).
2. **Operator-ratified factor-out** — if the operator rules the two records'
   concepts spec-committed (analogous to the T2 ratification) and authorizes a
   faithful factor-out, the CP plan revision pass specifies them. This requires an
   explicit operator ruling — v2.9 did NOT make it.

No silent absorption — no field set was invented. U-CP-04 may land partially
(default) or stay halted, at operator discretion.
