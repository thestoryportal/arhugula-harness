# Class 1 Tension — CP v2.8 batch blocked units (shared-cause cluster record)

**Status:** ✅ RESOLVED 2026-05-16 — see "RESOLUTION — CP plan v2.9" section below + "Audit reconciliation (2026-05-20)" footer + Phase A.1 confirmation (`.harness/Phase_A_1_Tension_Resolution_v1.md`, 2026-05-21). 10/11 batch units fully unblocked at CP plan v2.9 T2 X-AL-3 FACTOR-OUT; U-CP-04 upgraded PARTIAL-LAND → FULL-LAND at v2.10 R-2/W-2 ratification. Original HALT framing below preserved for historical traceability.
**Original Status (HALT — preserved for traceability):** 🛑 HALT — 11 CP units in the v2.8 L1–L3 batch cannot be landed.
**Filed:** 2026-05-16 (Phase 7 7b, CP axis-stream).
**Resolved:** 2026-05-16 (same-day; CP plan v2.9 + v2.10 absorption).
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

---

## RESOLUTION — CP plan v2.9 (2026-05-16)

`Implementation_Plan_Control_Plane_v2_9.md` (multi-body delta over v2.8) absorbs
the operator-ratified T2 X-AL-3 FACTOR-OUT resolution
(`.harness/xal3_resolution_recommendations.md`) and specifies the Pattern-D *tail*
structured types — `ProposedAction`, `ActionKind`, `ActionPayload`,
`FailedAttempt`, `Alternative`, `RetryHistory`, `StateSummary`, `RetryPolicy`,
`CPAuditLedgerEntry`/`CPSignedAuditLedgerEntry`, `LeadAgentPlan`, `VerifierResult`,
`OverlayResolution`, `WebhookConfig`, `WebhookPayload`, `HITLInvocation`,
`MaterialDiff` — each as a faithful factor-out of its committing spec section.
`InferenceRequest` unified to the v2.8 `ProviderAgnosticPayload`. The carrier-map
"Open — Class 1 halt" verdict that this record was filed against is STALE — T2
verdicts all 27/27 X-AL-3 candidates FACTOR-OUT and lifts the Class-1-halt framing.

### Per-unit verdict (the 11 batch-blocked units)

| Unit | v2.9 verdict | Detail |
|---|---|---|
| U-CP-04 | ⚠️ PARTIALLY UNBLOCKED | `RetryPolicy` specified (C-CP-03 §3.5) — lands. `RoutingManifest` **partial-lands**: `RoleRoutingBinding` / `WorkloadRoutingOverride` value-types stay Class 1 — see `.harness/class_1_tension_role_routing_binding_underspec.md`. |
| U-CP-05 | ✅ UNBLOCKED (transitive) | Root cause B+C — `InferenceRequest` unified to `ProviderAgnosticPayload` (landed at U-CP-00c); `RoutingManifest` from U-CP-04 partial-lands. Clears once U-CP-03/04 land. |
| U-CP-08 | ✅ UNBLOCKED (transitive) | Root cause B — v2.8-conformed body materializable; clears once U-CP-05 lands. |
| U-CP-09 | ✅ UNBLOCKED (transitive) | Root cause B — clears once U-CP-05 + U-CP-08 land. |
| U-CP-13 | ✅ UNBLOCKED | `HandoffContext` family (U-CP-30) + `HITLPlacement` deps now specified; clears once carrier deps land. |
| U-CP-14 | ✅ UNBLOCKED | `CPAuditLedgerEntry` / `CPSignedAuditLedgerEntry` specified at this unit (C-CP-16 §16.2 / C-CP-20 §20.4); name-collision with OD `AuditLedgerEntry` resolved. |
| U-CP-30 | ✅ UNBLOCKED | All 7 `HandoffContext`-family types specified (C-CP-13 §13.1/§13.4). Root cause A cleared. |
| U-CP-33 | ✅ UNBLOCKED | `LeadAgentPlan` specified as opaque `Mapping[str, Any]` (faithful — spec commits concept, not record). Root-cause-C U-CP-32 dep clears when U-CP-32 lands. |
| U-CP-38 | ✅ UNBLOCKED | `ProposedAction` specified at U-CP-30; clears once U-CP-30 lands. |
| U-CP-39 | ✅ UNBLOCKED (transitive) | `ProposedAction` specified; clears once U-CP-38 lands. |
| U-CP-44 | ✅ UNBLOCKED | `CPAuditLedgerEntry` / `CPSignedAuditLedgerEntry` specified at U-CP-14; consumes them via `[U-CP-14]`. (`SecretRef` from U-AS-20 is a separate fork-queue item, unchanged.) |

Also unblocked by v2.9 (in the v2.9-revised body set but not in this 11-unit batch
record): **U-CP-17** (`HITLInvocation` specified), **U-CP-22** (`MaterialDiff`
specified), **U-CP-41** (`VerifierResult` / `OverlayResolution` specified),
**U-CP-52** (`WebhookConfig` / `WebhookPayload` specified).

### Stays Class 1

- `RoleRoutingBinding`, `WorkloadRoutingOverride` — NOT T2-covered; no committing
  contract decomposes them. New record filed:
  `.harness/class_1_tension_role_routing_binding_underspec.md`. U-CP-04's
  `RoutingManifest` partial-lands; the two `Map` value-types are a forward carry.

**Status of this record:** the Pattern-D root cause A is RESOLVED for all
structured types except the two §0.5 sub-records. Root causes B and C clear
automatically as their blocking deps land (transitive). 10 of 11 units fully
unblocked; U-CP-04 partially unblocked.


---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** CP plan v2.9 filed (T2 X-AL-3 FACTOR-OUT resolution applied — Pattern-D types specified; 10/11 batch units unblocked). U-CP-04 partial-land separately tracked at role_routing_binding_underspec record (also RESOLVED).

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
