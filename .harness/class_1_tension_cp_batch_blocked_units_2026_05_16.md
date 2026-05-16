# Class 1 Tension — CP v2.8 batch blocked units (shared-cause cluster record)

**Status:** 🛑 HALT — 11 CP units in the v2.8 L1–L3 batch cannot be landed.
**Filed:** 2026-05-16 (Phase 7 7b, CP axis-stream).
**Scope:** the v2.8-batch units U-CP-04, 05, 08, 09, 13, 14, 30, 33, 38, 39, 44.

This is the canonical shared-cause record for the 11 blocked units. Per-unit
stub records (`class_1_tension_u_cp_NN_*.md`) point here.

## Root cause A — Pattern-D undeclared structured types (carrier-map "Open — Class 1 halt")

`Spec_Control_Plane_v1_3` declares no field set for a cluster of structured
record/handoff types the plan bodies consume at signature positions. The
shared-type carrier map (`.harness/shared_type_carrier_map.md`) and the
materializability audit (`.harness/materializability_audit_cp_plan.md`,
Pattern D) verdict these **Open — Class 1 halt**: inventing a field set is an
X-AL-3 design extension.

Affected types: `ProposedAction`, `ActionKind`, `ActionPayload`, `FailedAttempt`,
`Alternative`, `RetryHistory`, `RetryPolicy`, `RoleRoutingBinding`,
`WorkloadRoutingOverride`, `InferenceRequest`, `AuditLedgerEntry` /
`SignedAuditLedgerEntry`, `LeadAgentPlan`.

## Root cause B — dependency on a Root-cause-A-blocked unit

A unit whose own body is materializable but which `Depends on:` a unit blocked
by root cause A (transitive halt).

## Root cause C — dependency on an out-of-scope (not-yet-landed) unit

A unit citing a dep that is neither landed nor in this batch.

## Per-unit classification

| Unit | Root cause | Detail |
|---|---|---|
| U-CP-04 | A | `RoutingManifest` consumes `RoleRoutingBinding`, `WorkloadRoutingOverride`, `RetryPolicy` (Pattern-D, no spec field set) + `FallbackChain` from U-CP-09. |
| U-CP-05 | B + C | `route(request: InferenceRequest, …)` — `InferenceRequest` declared at U-CP-03 (not landed; not in batch). `Depends on: [U-CP-03, U-CP-00, U-CP-00b]` per v2.6 §0.12 — U-CP-03 unlanded. Also needs `RoutingManifest` from U-CP-04 (blocked). |
| U-CP-08 | B | v2.8 `Depends on: [U-CP-01, U-CP-05, U-CP-06, U-CP-07]` — U-CP-05 blocked. The v2.8-conformed `FallThroughCause` body is itself materializable; the dep chain is not. |
| U-CP-09 | B | `Depends on: [U-CP-02, U-CP-05, U-CP-07, U-CP-08, U-AS-30]` — U-CP-05 + U-CP-08 blocked. |
| U-CP-13 | A + B | `WorkflowManifestEntry` consumes `HITLPlacement` (U-CP-38, blocked) + `StepOverride.model_binding`; `Depends on:` U-CP-04 (blocked), U-CP-09 (blocked), U-CP-38 (blocked), U-CP-30 (blocked) per v2.6 §0.12. |
| U-CP-14 | B | `resolve_step_binding` consumes `WorkflowManifestEntry` / `StepOverride` / `StepEffectiveBinding` from U-CP-13 (blocked); `LedgerEntryRef` from U-CP-30 (blocked) per v2.6 §0.11.2. `AuditLedgerEntry` itself is F2-shaped (clean), but the U-CP-13 dep is the hard block. |
| U-CP-30 | A | `HandoffContext` / `ProposedAction` / `StateSummary` consume `ProposedAction`, `ActionKind`, `ActionPayload`, `FailedAttempt`, `Alternative`, `RetryHistory`, `ReferenceClass`, `ExternalReference` — Pattern-D, no spec field set. |
| U-CP-33 | C | `Depends on: [U-CP-32, …]` — U-CP-32 (span-hierarchy unit) is out of scope (L4–L8) and not landed. |
| U-CP-38 | A + B | `hitl_gate` / `HITLResult` consume `ProposedAction` (Pattern-D); `Depends on: U-CP-30` (blocked). |
| U-CP-39 | B | `rewrite_tool_call_to_hitl` consumes `ProposedAction` (Pattern-D) + `Depends on: U-CP-38` (blocked). |
| U-CP-44 | A | `sign_audit_entry` / `verify_audit_entry_signature` consume `AuditLedgerEntry` / `SignedAuditLedgerEntry` (Pattern-D, no spec field set); `SecretRef` from U-AS-20 (fork-queue item 14, contradicted verbatim claim). |

## Routing

Class 1 — halt-execution. Root cause A routes to design-substrate: the
Pattern-D structured types need their field sets specified (either a spec
revision committing the shapes, or — as v2.8 did for the 9 deferred types — a
faithful-factor-out plan revision if the operator ratifies the concepts as
spec-committed). Root causes B and C clear automatically once their blocking
deps land. No silent absorption — no field set was invented.

The 7 LAND-set units of this batch (U-CP-00c, 11, 12, 20, 24, 25, 29-partial,
34, 42) landed; the 11 units above are skipped pending resolution.
