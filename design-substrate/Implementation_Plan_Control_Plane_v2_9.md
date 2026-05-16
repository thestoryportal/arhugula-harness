# Implementation Plan — Control Plane v2.9

**Status:** Proposed

**Date:** 2026-05-16

**Revision:** v2.9 — Phase 7 sub-phase 7b in-CLI revision. **Specifies the Pattern-D *tail* structured types — the second cluster of CP record/handoff types still declared name-only in the plan bodies after v2.8.** v2.8 closed the 9 *deferred* structured shared types at the new L0 carrier U-CP-00c. But a second cluster of "Pattern-D" structured types — `HandoffContext`-family, `ProposedAction`, `FailedAttempt`/`Alternative`/`RetryHistory`, `StateSummary`, `RetryPolicy`, `CPAuditLedgerEntry`/`CPSignedAuditLedgerEntry`, `LeadAgentPlan`, `VerifierResult`/`OverlayResolution`, `WebhookConfig`/`WebhookPayload`, `HITLInvocation`, `MaterialDiff`, `ActionKind`, `InferenceRequest` — remained consumed at signature positions in the plan bodies with no concrete field schema, blocking 11 CP units (`.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md`). The batch-1 sub-agent halted on these citing the carrier map's "Open — Class 1 halt" verdict. **That verdict is STALE.** The operator-ratified T2 X-AL-3 resolution (`.harness/xal3_resolution_recommendations.md`) verdicts all 27/27 X-AL-3 candidates **FACTOR-OUT** — every type's concept is committed by an existing spec/ADR, only the declaration site was missing — and explicitly lifts the Class-1-halt framing for the CP structured-type cluster *and* `AuditLedgerEntry`. v2.9 specifies each tail type by faithful factor-out from its T2-cited committing spec section, traced byte-exact. v2.9 is a **multi-body delta** over v2.8: it revises the Signatures blocks of 8 existing unit bodies (U-CP-04/14/17/22/30/33/41/52) to add concrete field schemas — it is NOT a new carrier unit. Every other section is preserved verbatim from v2.8/v2.7/v2.6. Predecessor: v2.8 (9 deferred structured types + U-CP-08/U-CP-11 conformance).

**Revision date:** 2026-05-16

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain + §4.3 back-flow routing; `harness-cp/CLAUDE.md` §5; `implementation-planner` SKILL.md §8 revision-pass sub-mode; operator-ratified T2 X-AL-3 resolution (`.harness/xal3_resolution_recommendations.md`) — `ProposedAction`, `MaterialDiff`, `ParentRelation`, `HandoffContext`-family, `VerifierResult`, `OverlayResolution`, `WebhookConfig`, `WebhookPayload`, `HITLInvocation`, `LeadAgentPlan`, `FailedAttempt`/`Alternative`/`RetryHistory`, `CurrentState`(=`StateSummary`), `RetryPolicy`, `AuditLedgerEntry` all verdicted FACTOR-OUT (no design-substrate revision needed; the `implementation-planner` revision pass declares the faithful factor-out shape at the consuming carrier unit).

**Entry authorization:** Operator ratification 2026-05-15 of the T2 X-AL-3 FACTOR-OUT resolution (`.harness/xal3_resolution_recommendations.md`); operator task authorization 2026-05-16 to specify the Pattern-D tail structured types as a v2.9 revision pass.

---

## §0 Change-note

### §0.1 Trigger

After v2.8 closed the 9 *deferred* structured shared types at U-CP-00c, the batch-1 CP axis-stream sub-agent attempted the v2.8 L1–L3 batch and halted on a **second** cluster of structured types — the "Pattern-D tail" — still consumed name-only in the plan bodies (`.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md`, 🛑 HALT — 11 units). The halt cited the shared-type carrier map's "Open — Class 1 halt" verdict for these types (`.harness/shared_type_carrier_map.md` Disposition-4; `.harness/materializability_audit_cp_plan.md` Pattern D).

**That verdict is stale.** It predates the operator-ratified T2 X-AL-3 resolution. T2 (`.harness/xal3_resolution_recommendations.md`) verdicts all 27 X-AL-3 candidates **FACTOR-OUT: 27 of 27 (100%)** — "the cluster is a carrier-map gap, not a design-extension cluster … the T1 Disposition-4 'BLOCK until back-flow' framing over-escalated". T2 §"The 2 Class-1 halts — both dissolve into FACTOR-OUTs" explicitly lifts the Class-1-halt framing for the CP structured-type cluster and for `AuditLedgerEntry`. v2.6 §0.1 already records the T2 lift; this revision pass absorbs it into the affected unit bodies.

The carried items absorbed at this revision:

1. **The Pattern-D tail structured types.** Every type the blocked-units record names under "Root cause A" except the 9 already closed at v2.8 — see §0.3 for the full type list with per-type T2 verdict trace.
2. **`CurrentState` / `StateSummary` spelling unification.** T2 row `CurrentState`: "the CP audit's `CurrentState` is the spec-committed `StateSummary` concept under a plan spelling. Spelling unification recommended." v2.9 unifies to `StateSummary` (already the spelling at U-CP-30; no `CurrentState` spelling reappears).
3. **`InferenceRequest` / `ProviderAgnosticPayload` spelling unification.** `InferenceRequest` is consumed at U-CP-05/08 routing-call signature positions. It is a plan-spelling variant of the T2-covered `ProviderAgnosticPayload` (specified at v2.8 §0.3 as `{messages, tools, params}`). CP §1.1 commits the `(messages, tools, params)` 3-tuple as the routing/inference call surface; C-CP-01/02 use the inference-request and provider-agnostic-payload concepts interchangeably (both are the call-surface payload). v2.9 unifies — `InferenceRequest` = `ProviderAgnosticPayload` (the U-CP-00c type from v2.8) — analogous to the `CurrentState`=`StateSummary` unification.

### §0.2 Class + routing

The Pattern-D tail item was a Class 1 (plan signatures not at implementation-grade detail) per `CLAUDE.md` §4.3, recorded at `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md`. The operator-ratified T2 X-AL-3 resolution verdicts every member **FACTOR-OUT** — each type's *concept* is committed by an existing spec/ADR section, and specifying a faithful factor-out of the committing contract is **not** a design extension (no X-AL-3 violation; no design-substrate revision needed; T2 §"Consolidated design-substrate-revision list" — "**NONE**"). Routing target: this Phase-6 plan revision (in-CLI). For two sub-records that T2 does **not** cover — `RoleRoutingBinding`, `WorkloadRoutingOverride` — see §0.5; v2.9 does **not** extend the T2 ratification by analogy and leaves them Class 1.

### §0.3 The Pattern-D tail structured types — specified shapes (faithful factor-out, traced byte-exact)

Each shape below is a faithful factor-out of its T2-cited committing contract section. No member set or field is invented; where a contract defers a sub-shape to implementation discretion the factor-out adopts the spec's own opaque-vocabulary form (`Mapping[str, Any]` / opaque alias) — no extension. The carrier is the **consuming unit** named in the T2 row (multi-body delta — §0.6), not a new carrier unit.

| Type | Kind | Shape (specified) | Carrier unit | Committing contract (T2 row) |
|---|---|---|---|---|
| `ActionKind` | enum (3) | `{ TOOL_CALL, SUB_AGENT_DISPATCH, INFERENCE_STEP }` | U-CP-30 | T2 `ProposedAction` row + carrier map line 113 (decided inline-comment-enum promotion); C-CP-13 §13.1 `ProposedAction` constituent; C-CP-17 §17.1 placement triggers (tool-call / sub-agent-boundary) |
| `ActionPayload` | type alias | `Mapping[str, Any]` (opaque) | U-CP-30 | C-CP-16 / §17 — `ProposedAction` committing sections do **not** decompose the action-payload shape (§16/§17 reference `edited_proposal` / `edited_proposal_hash` only); kept opaque per §16.4 deferred clause. **Faithful — no invented field set.** |
| `ProposedAction` | record | `{ action_kind: ActionKind, payload: ActionPayload, brief: Optional[SubAgentBrief] }` | U-CP-30 | C-CP-16 §16.1 four-response palette (`approve`/`edit`/`reject` *of a proposed action*) + C-CP-17 §17 three-placement HITL; ADR-D5 §1.1 |
| `FailedAttempt` | record | `{ attempt_index: int, cause: str, attempted_at: str }` | U-CP-30 | C-CP-03 §3.5 `retry.*` namespace (`retry.attempt`, `retry.cause`) + C-CP-13 §13.4 — `HandoffContext.failed_attempts: List[FailedAttempt]` "prior sub-agent failures on the same task" |
| `Alternative` | record | `{ description: str, rejected_reason: str }` | U-CP-30 | C-CP-13 §13.1 — `HandoffContext.alternatives_considered: List[Alternative]` "lead's deliberation context" |
| `RetryHistory` | record | `{ attempts: List[FailedAttempt], retry_count: int, last_retry_cause: Optional[str] }` | U-CP-30 | C-CP-03 §3.5 `retry.*` namespace + C-CP-13 §13.1/§13.4 — `RetryHistory` **named in spec** ("`HandoffContext.retry_history: RetryHistory` — C9 retry primitives state per `retry.*` namespace at C-CP-03 §3.5") |
| `StateSummary` | record | `{ relevant_entries: List[LedgerEntryRef], summary_text: str, summary_hash: SHA256, idempotency_key: IdempotencyKey, external_references: List[ExternalReference] }` | U-CP-30 | C-CP-13 §13.4 — `StateSummary` committed by name and field-by-field. CP audit's `CurrentState` UNIFIED to this spelling (T2 `CurrentState` row). |
| `RetryPolicy` | record | `{ max_attempts: int, backoff: str, jitter: str }` | U-CP-04 | C-CP-03 §3 chain-advancement + §3.5 `retry.*` namespace (`retry.policy` = "full-jitter default per Cluster 4 §2.2.7 [HIGH]"); hand-rolled retry per `CLAUDE.md` §3.2 |
| `CPAuditLedgerEntry` | record | `{ action_id, gate_level, response, edited_proposal_hash?, rejection_reason_hash?, response_text_hash?, timestamp, prior_event_hash }` | U-CP-14 | C-CP-16 §16.2 — per-response audit-ledger entry shape committed verbatim (T2 `AuditLedgerEntry @ CP` row). **Renamed `CPAuditLedgerEntry` — name-collision resolution, see §0.5.1.** |
| `CPSignedAuditLedgerEntry` | record | `CPAuditLedgerEntry` + `{ audit_signature_sha256, audit_signature_value, audit_signature_algorithm, audit_signature_key_id, audit_signature_key_period }` | U-CP-14 | C-CP-20 §20.1 + §20.4 — per-persona-tier audit-ledger cryptographic shape (cited inside the T2 `AuditLedgerEntry` row). **Renamed `CPSignedAuditLedgerEntry` — §0.5.1.** |
| `LeadAgentPlan` | type alias | `Mapping[str, Any]` (opaque) | U-CP-33 | ADR-D4 v1.1 + C-CP-13 §13.3 + C-CP-14 §14.4 step 1 ("persist lead-agent's plan"). The spec commits the *concept* (lead-agent deliberation artifact persisted to filesystem) but **does not decompose a `LeadAgentPlan` record** — opaque alias is the faithful factor-out (§0.5.2). |
| `VerifierResult` | record | `{ verifier_verdict: VerifierVerdict, validator_fail_class: Optional[str], verifier_span_id: str }` | U-CP-41 | C-CP-18 §18.4 two-agent-observer meta-class — "verifier agreement and disagreement both surface as inputs to the operator response palette"; "verifier output emits `validator.fail.*` span attributes per C-CP-21 §21.5" |
| `OverlayResolution` | record | `{ overlay_outcome: OverlayOutcome, gate_invoked: bool, palette_restricted: bool }` | U-CP-41 | C-CP-18 §18.3 both-by-tier per-tool overlay — `tier ∈ {auto, ask, deny}` determines which actions invoke HITL gate; auto → no gate, ask → cell synchrony delivers gate, deny → structurally rejected |
| `WebhookConfig` | record | `{ webhook_id: str, endpoint_url: str, timeout: Duration, degradation_mode: str }` | U-CP-52 | C-CP-18 §18.5 + C-CP-21 §21.8 — webhook ingress for durable-async cells; idempotency-keyed signal delivery; timeout-degradation mode |
| `WebhookPayload` | record | `{ approval_id: str, idempotency_key: IdempotencyKey, gate_evaluation_ref: EntryID, payload_body: Mapping[str, Any] }` | U-CP-52 | C-CP-18 §18 (C-CP-18) + C-CP-21 §21.8 — "`(approval_id, idempotency_key)` checked against the ledger before signal application" |
| `HITLInvocation` | record | `{ invocation_id: str, placement: str, handoff_context: HandoffContext, response_palette: Set[str], timeout: Optional[Duration], cascade_policy: str, opened_at: str }` | U-CP-17 | C-CP-17 §17.1.1 `hitl_gate(...)` argument set + C-CP-16 §16.4 `hitl.invocation.responded` event + C-CP-20 §20.6 / C-CP-22 §22.3 `hitl.invocation.opened` event |
| `MaterialDiff` | record | `{ reference: ExternalReference, prior_snapshot: bytes, current_value: bytes, is_material: bool }` | U-CP-22 | C-CP-22 §22.2 — material-diff detection contract committed explicitly + §22.1 `diff_set.add((external_reference, prior_snapshot, current_value))` |

`InferenceRequest` is **not** a new type — it is unified to the v2.8 U-CP-00c `ProviderAgnosticPayload` (§0.1 item 3); no row above.

#### §0.3.1 Per-type decision notes

- **`ActionKind` — enum promotion (decided).** Carrier map line 113 records `ActionKind` as a *decided* inline-comment-enum promotion — the value set (`{TOOL_CALL, SUB_AGENT_DISPATCH, INFERENCE_STEP}`) is already present verbatim in the U-CP-30 v2.1 plan-body comment (`#### U-CP-30` Signatures: `action_kind : ActionKind // {TOOL_CALL, SUB_AGENT_DISPATCH, INFERENCE_STEP}`). v2.9 promotes the comment to a real enum. The three values trace to the C-CP-17 §17.1 placement-trigger taxonomy (tool-call, sub-agent-boundary handoff) + the C-CP-13 §13.1 `ProposedAction` constituent. No value invented.
- **`ActionPayload` — opaque, NOT in T2 (decided faithful).** `ActionPayload` is a constituent of `ProposedAction` but is **not** a named T2 candidate. Per the task's not-in-T2 discipline: CP §16/§17 — the `ProposedAction` committing sections — reference `edited_proposal: Optional<ProposedAction>` and `edited_proposal_hash` (§16.2) but **never characterize the action-payload field shape**; §16.4 carries an explicit deferred clause. The faithful factor-out is the spec's own opaque vocabulary — `Mapping[str, Any]` — exactly as v2.8 §0.3 treated `ProviderAgnosticPayload`'s sub-mappings. No field set is invented; `ActionPayload` does **not** stay Class 1 because the *opaque* shape is itself a faithful, materializable factor-out (no guess).
- **`StateSummary` / `CurrentState` unification (T2-recommended).** T2's `CurrentState` row: the CP audit's `CurrentState` IS the C-CP-13 §13.4 `StateSummary` under a plan spelling. The U-CP-30 v2.1 body already declares `StateSummary` (5 fields); no `CurrentState` spelling appears in any v2.9-scope body. v2.9 records the unification; nothing renamed (the canonical spelling was already `StateSummary`).
- **`CPAuditLedgerEntry` shape — one record, response-conditional optional fields.** C-CP-16 §16.2 enumerates four response-class rows: `approve` carries `(action_id, gate_level, response, timestamp, prior_event_hash)`; `edit` adds `edited_proposal_hash`; `reject` adds `rejection_reason_hash?`; `respond` adds `response_text_hash`. §16.2 reads as **one schema with response-conditional hash fields** (not a tagged union of four records). v2.9 declares one `CPAuditLedgerEntry` record with the three response-specific hash fields `Optional` — `edited_proposal_hash` populated iff `response = edit`, `rejection_reason_hash` iff `reject`, `response_text_hash` iff `respond`. The acceptance criterion pins the per-response population rule. No field invented beyond the §16.2 table.
- **`CPSignedAuditLedgerEntry`** — C-CP-20 §20.1 commits the per-persona-tier cryptographic shape; §20.4 enumerates the seven `audit.*` attributes. `CPSignedAuditLedgerEntry` = `CPAuditLedgerEntry` + the five signature-bearing `audit.signature.*` attributes from §20.4 (`audit.signature.sha256`, `audit.signature.value`, `audit.signature.algorithm`, `audit.signature.key_id`, `audit.signature.key_period`). `audit.signature.prior_hash` is the chain link already carried by `CPAuditLedgerEntry.prior_event_hash` (§16.2 + §20.4 join); `audit.actor.id` is the `action_id`-adjacent actor — homed at the F2 `StateLedgerEntry` shape, not re-lifted here. v2.9 carries exactly the five signature attributes that are structurally added at the cryptographic tier.
- **`LeadAgentPlan` — opaque, NOT decomposed by spec (decided faithful).** ADR-D4 v1.1 + C-CP-13 §13.3 commit the lead-agent role and brief-authoring model binding; C-CP-14 §14.4 step 1 commits "persist lead-agent's plan to filesystem (CoALA episodic memory)". The spec commits the *concept* (a lead-agent deliberation artifact that is persisted and cache-warmed) but **does not characterize a `LeadAgentPlan` record shape** — §13.2 characterizes `SubAgentBrief` (4 fields, a distinct type) and §14.4 is a procedure. The U-CP-33 v2.1 body declared `LeadAgentPlan` name-only. Per the not-in-spec-decomposition discipline: the faithful factor-out is the opaque alias `Mapping[str, Any]` (the §1.4 / §16.4 deferred-to-implementation-discretion vocabulary) — **not** an invented `{plan_text, breakpoint_id, siblings}` record. `LeadAgentPlan` does **not** stay Class 1: the opaque shape is materializable and faithful (`pyright` resolves it; the cache-warmup protocol consumes it as a persisted blob). U-CP-33 is unblocked.
- **`VerifierResult` / `OverlayResolution`** — C-CP-18 §18.3/§18.4 commit the both-by-tier overlay outcomes and the two-agent-observer verifier-output concept. `VerifierResult` carries the verifier verdict (agreement/disagreement — §18.4 "verifier agreement and disagreement both surface as inputs to the operator response palette"), the optional `validator.fail.*` class (§18.4 "verifier output emits `validator.fail.*` span attributes per C-CP-21 §21.5" — domain is the C-CP-21 §21.5 5-value `validator.fail.class` set), and the verifier span id (§18.4 "`subagent.span[verifier]` per C-CP-14 §14.1"). `OverlayResolution` carries the three §18.3 overlay outcomes mapped to a discriminated `OverlayOutcome` (`auto` → no gate, `ask` → gate via cell synchrony, `deny` → structural reject) plus the `gate_invoked` / `palette_restricted` booleans the §18.3 audit-composition row and C-CP-19 §19.4 palette-restriction commit. The `VerifierVerdict` / `OverlayOutcome` constituent enums are declared at U-CP-41 (verifier/overlay-specific — not shared, not homed at U-CP-00c).
- **`WebhookConfig` / `WebhookPayload`** — C-CP-21 §21.8 commits the webhook-delivery contract: "Webhook ingress for durable-async cells MUST use idempotency-keyed signal delivery composed against F2 state-ledger entry shape per C-IS-05: `(approval_id, idempotency_key)` checked against the ledger before signal application". `WebhookConfig` is the per-webhook delivery descriptor (id, endpoint, timeout per §17.1.1 `hitl_gate` timeout, degradation mode per §21.8 table); `WebhookPayload` is the inbound-signal record keyed by the §21.8 `(approval_id, idempotency_key)` pair plus the `gate_evaluation_ref` join the U-CP-52 v2.1 body's `WebhookDeliveryEvent` already carries. Payload body kept opaque (`Mapping[str, Any]`) — §21.8 deferred clause: "specific webhook idempotency-key extraction from inbound signal payload" is implementation-discretion.
- **`HITLInvocation`** — the *opener-side* record (distinct from the §17.1.1 `HITLResult`, which is the *result-side* record already concretely specified in the spec). C-CP-20 §20.6 + C-CP-22 §22.3 reference the `hitl.invocation.opened` event with `hitl.invocation.handoff_context_size_bytes`; the opener field set is the C-CP-17 §17.1.1 `hitl_gate(...)` argument set (`placement`, `handoff_context`, `response_palette`, `timeout`, `cascade_policy`) plus an `invocation_id` and `opened_at` timestamp. `HITLInvocation` is homed at U-CP-17 (the HITL primitive unit per T2) and cross-cluster-consumed by U-CP-52 via the existing `[U-CP-17]` edge (v2.6 §0.11.5).
- **`MaterialDiff`** — C-CP-22 §22.2 commits the material-diff detection contract by name and §22.1 gives the diff-set tuple verbatim: `diff_set.add((external_reference, prior_snapshot, current_value))`. `MaterialDiff` factors out the tuple plus the `is_material` boolean the §22.2 per-reference-class predicate table produces. The `ExternalReference` constituent is already declared at U-CP-30 (v2.1 body) — `MaterialDiff` consumes it via the within-axis edge.

### §0.4 Carrier decision — multi-body delta, NO new carrier unit

v2.9 is **not** a new foundational carrier unit (contrast v2.8's U-CP-00c). Each Pattern-D tail type is homed at its **consuming carrier unit** — the unit whose body already declares the type name-only in a Signatures block — per the T2 carrier-row assignment and the `implementation-planner` SKILL.md §3.1 single-coherent-change rule (each type belongs to the unit that owns its surface):

| Carrier unit | Types homed (v2.9) |
|---|---|
| U-CP-04 | `RetryPolicy` |
| U-CP-14 | `CPAuditLedgerEntry`, `CPSignedAuditLedgerEntry` |
| U-CP-17 | `HITLInvocation` |
| U-CP-22 | `MaterialDiff` |
| U-CP-30 | `ActionKind`, `ActionPayload`, `ProposedAction`, `FailedAttempt`, `Alternative`, `RetryHistory`, `StateSummary` |
| U-CP-33 | `LeadAgentPlan` |
| U-CP-41 | `VerifierResult`, `OverlayResolution` (+ constituent enums `VerifierVerdict`, `OverlayOutcome`) |
| U-CP-52 | `WebhookConfig`, `WebhookPayload` |

No type is re-homed to `harness-core` or to U-CP-00c — each is a CP-axis routing/handoff/HITL/audit primitive consumed within its own carrier unit's cluster (with the one cross-cluster exception of `HITLInvocation`, U-CP-17 → U-CP-52, via the pre-existing `[U-CP-17]` edge).

### §0.5 Two sub-records left Class 1 — `RoleRoutingBinding`, `WorkloadRoutingOverride`

`RoleRoutingBinding` and `WorkloadRoutingOverride` are constituents of U-CP-04's `RoutingManifest` (`per_role_bindings: Map<AgentRole, RoleRoutingBinding>`, `per_workload_overrides: Map<WorkloadClass, WorkloadRoutingOverride>`). They are **NOT** T2 candidates — T2's carrier map only "proposed" them; no T2 verdict row covers them. Per the task's not-in-T2 discipline (DO NOT extend the ratification by analogy):

- **`WorkflowManifestEntry` (C-CP-06 §6.1) does NOT decompose these sub-records.** §6.1's manifest-entry shape names `workflow_class`, `engine_class`, `f3_invocation_default`, `routing_layer_budgets`, `fallback_chain`, `topology`, `hitl_placements` — it commits **no** `per_role_bindings` / `per_workload_overrides` sub-record. C-CP-01 §1.3 gives the authoring grain "per agent role × per workflow class × per step" in prose but enumerates no `RoleRoutingBinding` / `WorkloadRoutingOverride` field set. The two records originate in the v2.1 U-CP-04 plan body — they are **plan-side**, not spec-committed.
- **Verdict: stay Class 1.** The field sets are genuinely uncommitted; inventing them would be an X-AL-3 design extension. v2.9 files `.harness/class_1_tension_role_routing_binding_underspec.md` (covering both records) and records here that **U-CP-04's `RoutingManifest` is PARTIALLY blocked**: `RetryPolicy` and `fallback_chains` materialize; `per_role_bindings` and `per_workload_overrides` cannot. U-CP-04 may land in a partial form (see §2A.U-CP-04 acceptance criterion 5) or stay halted at operator discretion — the v2.9 default is partial-land with the two `Map` fields' value-types left as a forward Class 1 carry.

#### §0.5.1 `AuditLedgerEntry` name-collision resolution — `CPAuditLedgerEntry` / `CPSignedAuditLedgerEntry`

`harness-od` (U-OD-00) has **already landed** an `AuditLedgerEntry` — a different shape, the OD-local audit-ledger family. T2 (`AuditLedgerEntry @ CP` row + §"The 2 Class-1 halts" item 2) is explicit: CP's audit-ledger entry is a **parallel sibling family**, CP-spec-owned (C-CP-16 §16.2 / C-CP-20 §20.1), composing against the IS-exported `StateLedgerEntry` shape via the existing CP→IS edges — it is **not** OD's audit-ledger schema, and CP→OD stays foreclosed (CXA matrix CP→OD = 0 unchanged). To avoid a nominal-type collision in the workspace, v2.9 **names the CP types distinctly**: `CPAuditLedgerEntry` and `CPSignedAuditLedgerEntry`, homed in `harness-cp` at the U-CP-14 carrier. No import of, and no structural reconciliation with, the OD `AuditLedgerEntry`. This naming decision is binding for all v2.9-scope bodies and forward CP units (U-CP-27/44 consume `CPAuditLedgerEntry` under the new name).

#### §0.5.2 `LeadAgentPlan` — opaque, unblocks U-CP-33

Recorded at §0.3.1: `LeadAgentPlan` is specified as the opaque alias `Mapping[str, Any]` — a faithful factor-out of the C-CP-14 §14.4 "persist lead-agent's plan" concept, not an invented record. U-CP-33 is **unblocked** (it consumes the plan as a persisted blob; the cache-warmup protocol does not field-access it). No Class 1 record filed for `LeadAgentPlan`.

#### §0.5.3 `MCPTrustTier` reconciliation carry — Phase C note

`MCPTrustTier` landed at U-CP-00c (v2.8) as `{ LEVEL_0_REFUSE_REMOTE, LEVEL_1_SIGNED_PINNED, LEVEL_2_SANDBOX_ALL, LEVEL_3_ALLOW_WITH_AUDIT }` — byte-exact with `Spec_Action_Surface_v1.md` C-AS-10 §10.3. No v2.9-scope unit body declares an MCP-trust enum, so no reconciliation is applied at this revision. **Carry for Phase C:** if U-CP-43's body (5-axis gate composition; consumes `MCPTrustTier` + `Axis`) declares a divergent `TIER_1..4` MCP-trust enum, the Phase C plan/landing pass MUST reconcile it to the landed U-CP-00c `MCPTrustTier` (`LEVEL_*` form) — U-CP-43 consumes U-CP-00c's `MCPTrustTier` via the `[U-CP-00c]` edge (v2.8 §0.5), **no re-declaration**. This carry is informational; it has no v2.9 body consequence.

### §0.6 Changes at v2.9

v2.9 is a multi-body delta. It revises the Signatures block (and, where the new shapes change a stated field count, the matching acceptance criteria) of **8 existing unit bodies**. Every revised section is enumerated here:

| Site | v2.8 | v2.9 |
|---|---|---|
| §2A — U-CP-04 body | `RoutingManifest` consumes name-only `RetryPolicy` / `RoleRoutingBinding` / `WorkloadRoutingOverride` | **Revised body** — `RetryPolicy` specified (record, 3 fields, C-CP-03 §3.5); `RoleRoutingBinding` / `WorkloadRoutingOverride` left Class 1 (§0.5); `RoutingManifest` partial-land acceptance criterion added |
| §2A — U-CP-14 body | `AuditLedgerEntry` consumed name-only at `emit_override_audit_entry` | **Revised body** — `CPAuditLedgerEntry` + `CPSignedAuditLedgerEntry` specified (C-CP-16 §16.2 / C-CP-20 §20.1+§20.4); name-collision resolution §0.5.1 |
| §2A — U-CP-17 body | `HITLInvocation` not yet declared (consumed name-only at U-CP-52) | **Revised body** — `HITLInvocation` specified (opener-side record, C-CP-17 §17.1.1 + §16.4 + §20.6) |
| §2A — U-CP-22 body | `MaterialDiff` consumed name-only | **Revised body** — `MaterialDiff` specified (record, C-CP-22 §22.2/§22.1) |
| §2A — U-CP-30 body | `ProposedAction` / `ActionKind` / `ActionPayload` / `FailedAttempt` / `Alternative` / `RetryHistory` / `StateSummary` declared name-only or comment-only | **Revised body** — all 7 specified (C-CP-13 §13.1/§13.4 + C-CP-16/§17 + C-CP-03 §3.5); `ActionKind` enum-promoted; `ActionPayload` / `StateSummary` per §0.3 |
| §2A — U-CP-33 body | `LeadAgentPlan` consumed name-only | **Revised body** — `LeadAgentPlan` specified as opaque `Mapping[str, Any]` (§0.5.2) |
| §2A — U-CP-41 body | `VerifierResult` / `OverlayResolution` consumed name-only at function returns | **Revised body** — both specified (records, C-CP-18 §18.3/§18.4) + constituent enums `VerifierVerdict` / `OverlayOutcome` |
| §2A — U-CP-52 body | `WebhookConfig` / `WebhookPayload` consumed name-only at `deliver_webhook` | **Revised body** — both specified (records, C-CP-18 §18.5 / C-CP-21 §21.8) |
| §0.1 spelling unification | — | `InferenceRequest` = `ProviderAgnosticPayload` (U-CP-00c); `CurrentState` = `StateSummary` |
| §11.1 registry | Pattern-D tail rows absent / carrier-blank | Pattern-D tail rows added with v2.9-specified shapes (see §11.1 delta) |

**No new Class 3 informational item logged at this pass.** One new Class 1 record filed: `.harness/class_1_tension_role_routing_binding_underspec.md` (§0.5).

### §0.7 Sections preserved verbatim from v2.8/v2.7/v2.6

All of §0 (v2.6 + v2.7 + v2.8 change-notes), §1, §2.0 / §2.0b / §2.0c (U-CP-00 / U-CP-00b / U-CP-00c bodies), §2.1 U-CP-08 (v2.8-conformed) and §2.2 U-CP-11 (v2.8-conformed), and every unit body **except** the 8 revised at §2A below (U-CP-04, U-CP-14, U-CP-17, U-CP-22, U-CP-30, U-CP-33, U-CP-41, U-CP-52). §11 except the §11.1 registry rows enumerated at the §11.1 delta, §[carry-forwards], §[traceability], §[coherence pass], and any other section carried in v2.8/v2.7/v2.6 are preserved verbatim. The dependency graph is unchanged: every type homed at v2.9 lives at a unit that already consumes it, so no new inter-unit edge is created (the single cross-cluster edge `U-CP-52 → U-CP-17` for `HITLInvocation` already exists per v2.6 §0.11.5). The DAG remains acyclic.

---

## §2A Revised unit bodies — Pattern-D tail structured-type specification [REVISED — v2.9]

Each body below revises **only** its Signatures block (and the acceptance criteria that pin a stated field count or value set). All other content — `Implements`, `Depends on`, `Inputs`, `Files affected`, `Cross-axis substrate consumed`, `Tests`, `Rollback boundary` — is preserved verbatim from the v2.8/v2.7/v2.6 body unless explicitly noted. The revision is the faithful factor-out of the named Pattern-D tail types per §0.3.

### §2A — U-CP-04 [REVISED — v2.9]

#### U-CP-04 — Implement routing manifest residence (v2.9 — `RetryPolicy` specified as a faithful factor-out of C-CP-03 §3.5; `RoleRoutingBinding` / `WorkloadRoutingOverride` left Class 1 per §0.5 — `RoutingManifest` partial-land)

[v2.1-introduced unit; Root-cause-A blocked at the v2.8 batch per `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md`. **v2.9 factor-out delta.** `RetryPolicy` is a T2 FACTOR-OUT (T2 `RetryPolicy` row — C-CP-03 §3 + §3.5 `retry.*` namespace); v2.9 specifies it. `RoleRoutingBinding` / `WorkloadRoutingOverride` are NOT T2 candidates and their field sets are uncommitted (C-CP-06 §6.1 does not decompose them; C-CP-01 §1.3 gives prose grain only) — they stay Class 1 per §0.5; `.harness/class_1_tension_role_routing_binding_underspec.md` filed. `RoutingManifest` partial-lands. All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-01 §1.3] (+ C-CP-03 §3.5 for `RetryPolicy` per the v2.9 factor-out)

**Depends on:** [U-CP-01, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS), U-IS-06 (cross-axis: IS)]

**Inputs:** `routing.*` namespace (U-CP-01); filesystem path contract (U-IS-01 `PathClass`); path-resolver (U-IS-02); per-deployment-surface storage residence (U-IS-06).

**Files affected:** CP-axis routing manifest residence (logical: `routing-manifest-residence`); CP-axis routing-manifest schema declaration (logical: `routing-manifest-schema`); CP-axis retry-policy record (logical: `retry-policy-record`).

**Cross-axis substrate consumed.** `FILESYSTEM_PATH_CONTRACT_EXPORT` (C-IS-10 §10.4 → U-IS-01, U-IS-02) for canonical manifest residence; per-deployment-surface storage classification via U-IS-06.

**Signatures:**

```
record RetryPolicy {
  max_attempts : int     // retry-attempt cap per C-CP-03 §3 chain-advancement
  backoff      : str     // backoff strategy token; "full-jitter" default per
                         //   C-CP-03 §3.5 `retry.policy` ("full-jitter default
                         //   per Cluster 4 §2.2.7 [HIGH]")
  jitter       : str     // jitter mode token; composes with `backoff`
}
// Faithful factor-out of the C-CP-03 §3 chain-advancement contract + the §3.5
// `retry.*` namespace `retry.policy` attribute (full-jitter default). Hand-rolled
// retry per CLAUDE.md §3.2 — NO tenacity/pybreaker. No field invented beyond the
// §3.5 retry-policy vocabulary.

record RoutingManifest {
  manifest_version       : int
  per_role_bindings      : Map<AgentRole, RoleRoutingBinding>      // ⚠ Class 1 — §0.5
  per_workload_overrides : Map<WorkloadClass, WorkloadRoutingOverride>  // ⚠ Class 1 — §0.5
  fallback_chains        : List<FallbackChain>             // populated per C-CP-04
  retry_policies         : Map<ToolName, RetryPolicy>      // populated per C-CP-03 §3.5
}
// `RoleRoutingBinding` / `WorkloadRoutingOverride` value-types remain Class 1
// (NOT T2-covered; C-CP-06 §6.1 does not decompose them). RoutingManifest
// partial-lands — see acceptance criterion 5.

function load_routing_manifest(path: FilesystemPath) -> RoutingManifest
function validate_routing_manifest(manifest: RoutingManifest) -> Result<Unit, ValidationError>
```

**Acceptance criteria:**
1. `RoutingManifest` schema declares exactly five top-level fields per C-CP-01 §1.3 + cross-references to C-CP-03 §3.5 + C-CP-04 §4.1.
2. Manifest residence path resolves via U-IS-02 against U-IS-01 `PathClass`; per-deployment-surface residence delegates to U-IS-06.
3. `validate_routing_manifest` returns `Err` if any `RoleRoutingBinding` cites a model not present in U-AS-29 model-binding catalog (cross-axis check; runtime-deferred).
4. Manifest format (JSON vs YAML vs TOML) deferred to implementation discretion per spec §1.3 deferred list.
5. **`RetryPolicy` declares exactly three fields `max_attempts: int`, `backoff: str`, `jitter: str` — a faithful factor-out of the C-CP-03 §3.5 `retry.policy` full-jitter-default vocabulary; no field invented.** `RoutingManifest` **partial-lands**: `manifest_version`, `fallback_chains`, `retry_policies` materialize; `per_role_bindings` and `per_workload_overrides` value-types (`RoleRoutingBinding` / `WorkloadRoutingOverride`) are a forward Class 1 carry per `.harness/class_1_tension_role_routing_binding_underspec.md` — the two `Map` fields land with their value-type as a deferred opaque placeholder pending Class 1 resolution. No `RoleRoutingBinding` / `WorkloadRoutingOverride` field set is invented.

**Tests:** `test_routing_manifest_five_fields`, `test_load_via_u_is_02`, `test_validate_rejects_unknown_model`, `test_format_deferred`, `test_retry_policy_three_fields_byte_exact_cp_03_3_5`, `test_role_routing_binding_value_type_deferred` (regression — no invented field set on the two `Map` value-types).

**Rollback boundary:** Revert `RoutingManifest` schema + `RetryPolicy` record + residence binding. Routing-manifest-driven binding at U-CP-05 loses canonical persistence; runtime routing degrades to hardcoded defaults. Cross-axis IS edges to U-IS-01, U-IS-02, U-IS-06 release. A single coherent revert.

---

### §2A — U-CP-14 [REVISED — v2.9]

#### U-CP-14 — Implement per-step override evaluator + audit-ledger entry composition (v2.9 — `CPAuditLedgerEntry` + `CPSignedAuditLedgerEntry` specified as faithful factor-outs of C-CP-16 §16.2 / C-CP-20 §20.1+§20.4; CP-distinct naming per the §0.5.1 name-collision resolution)

[v2.1-introduced unit; Root-cause-B blocked at the v2.8 batch (the U-CP-13 dep is the hard block; `AuditLedgerEntry` itself is the §16.2 factor-out). **v2.9 factor-out delta.** T2 (`AuditLedgerEntry @ CP` row) verdicts CP's audit-ledger entry FACTOR-OUT — C-CP-16 §16.2 commits the per-response shape verbatim; §20 commits the cryptographic shape. v2.9 specifies both. **Name-collision resolution (§0.5.1):** `harness-od` U-OD-00 already landed a distinct `AuditLedgerEntry`; the CP types are renamed `CPAuditLedgerEntry` / `CPSignedAuditLedgerEntry`, homed in `harness-cp`. All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-06 §6.2] (+ C-CP-16 §16.2 + C-CP-20 §20.1, §20.4 for the audit-entry factor-out)

**Depends on:** [U-CP-13, U-CP-15, U-IS-07 (cross-axis: IS), U-IS-08 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-11 (cross-axis: IS)]

**Inputs:** Workflow manifest entry (U-CP-13); `EngineClass` enum (U-CP-15); F2 substrate (U-IS-07, U-IS-08, U-IS-09, U-IS-11 cross-axis).

**Files affected:** CP-axis per-step override evaluator (logical: `per-step-override-evaluator`); CP-axis override audit-ledger entry composition (logical: `override-audit-ledger-composition`); CP-axis audit-ledger entry records (logical: `cp-audit-ledger-entry`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` + `JSONL_EVENT_LEDGER_FORMAT_EXPORT` (C-IS-10 §10.1, §10.3, §10.5) for audit-ledger entry composition.

**Signatures:**

```
record CPAuditLedgerEntry {
  action_id            : ActionID
  gate_level           : GateLevel                  // {auto, ask, deny} per C-CP-19 §19.1
  response             : str                        // ∈ {approve, edit, reject, respond}
                                                     //   per C-CP-16 §16.1
  edited_proposal_hash : Optional<SHA256>            // populated iff response = edit  (§16.2 row 2)
  rejection_reason_hash: Optional<SHA256>            // populated iff response = reject (§16.2 row 3)
  response_text_hash   : Optional<SHA256>            // populated iff response = respond (§16.2 row 4)
  timestamp            : ISO8601
  prior_event_hash     : SHA256                      // hash-chain link per C-IS-06
}
// One record with response-conditional optional hash fields — a faithful
// factor-out of the C-CP-16 §16.2 four-row per-response audit-ledger entry
// table. CP-spec-owned (T2 `AuditLedgerEntry @ CP` row); composes against the
// IS-exported StateLedgerEntry shape via the existing CP→IS edges. Renamed
// CP-distinct per §0.5.1 — NOT the OD-local AuditLedgerEntry (U-OD-00); no
// import of, no reconciliation with, the OD type.

record CPSignedAuditLedgerEntry {
  entry                   : CPAuditLedgerEntry
  audit_signature_sha256  : str                      // hex-64; the signed hash, §20.4
  audit_signature_value   : bytes                    // per-entry signature, §20.4
  audit_signature_algorithm : str                    // ∈ {ed25519, ecdsa-p256, rsa-pss-2048}, §20.4
  audit_signature_key_id  : str                      // F5 signing-key identifier, §20.4
  audit_signature_key_period : int                   // monotonic key-period, §20.4
}
// CPAuditLedgerEntry + the five signature-bearing audit.signature.* attributes
// from C-CP-20 §20.4. Faithful factor-out of the C-CP-20 §20.1 per-persona-tier
// cryptographic shape; emitted at multi-tenant-compliance (and team-binding opt-in).

function resolve_step_binding(
    manifest_entry: WorkflowManifestEntry,
    step_id: StepID
) -> StepEffectiveBinding
    // applies per_step_overrides over manifest_entry defaults
    // emits audit-ledger entry per ADR-F2 audit composition when override applied

record StepEffectiveBinding {
  step_id            : StepID
  model_binding      : ModelBinding                  // effective (override or default)
  engine_class       : EngineClass
  hitl_placement     : Optional<HITLPlacement>
  override_applied   : bool
  override_audit_ref : Optional<LedgerEntryRef>      // when override_applied = true
}

function emit_override_audit_entry(
    workflow_id: string,
    step_id: StepID,
    override: StepOverride,
    actor: ActorIdentity
) -> CPAuditLedgerEntry
    // delegates F2 six-field construction to U-IS-07/08/09/11
```

**Acceptance criteria:**
1. `resolve_step_binding` returns the effective binding combining manifest defaults + per-step override; override field-by-field; no field-set substitution.
2. When override applied, `override_audit_ref` populated by `emit_override_audit_entry` per F2 audit composition; audit entry shape per U-IS-07 six-field shape with `action_id = workflow_id || step_id`.
3. `emit_override_audit_entry` delegates canonicalize+hash to U-IS-08; chain construction to U-IS-09; append to U-IS-11.
4. Override evaluator is deterministic given inputs.
5. **`CPAuditLedgerEntry` declares eight fields per C-CP-16 §16.2 — `action_id`, `gate_level`, `response`, three `Optional` response-specific hash fields, `timestamp`, `prior_event_hash`.** The response-conditional population rule holds: `edited_proposal_hash` is populated iff `response = edit`, `rejection_reason_hash` iff `reject`, `response_text_hash` iff `respond`; all three absent for `approve`. No field invented beyond the §16.2 table.
6. **`CPSignedAuditLedgerEntry` wraps `CPAuditLedgerEntry` plus exactly five `audit.signature.*` fields per C-CP-20 §20.4** (`sha256`, `value`, `algorithm`, `key_id`, `key_period`). The two CP audit types are nominally distinct from the OD-landed `AuditLedgerEntry` (no import, no structural reconciliation per §0.5.1).

**Tests:** `test_resolve_step_binding_field_by_field_override`, `test_audit_ref_populated_on_override`, `test_audit_entry_action_id_composition`, `test_delegates_to_u_is_07_08_09_11`, `test_cp_audit_ledger_entry_eight_fields_byte_exact_cp_16_2`, `test_cp_audit_entry_response_conditional_hash_population`, `test_cp_signed_audit_entry_five_signature_fields_cp_20_4`, `test_cp_audit_types_distinct_from_od_audit_ledger_entry`.

**Rollback boundary:** Revert per-step override evaluator + audit composition + the two CP audit-entry records. Pipeline-automation per-stage customization loses runtime evaluation; override audit trail dissolves; U-CP-27/44 lose the `CPAuditLedgerEntry` carrier. Cross-axis IS edges to U-IS-07, U-IS-08, U-IS-09, U-IS-11 release. A single coherent revert.

---

### §2A — U-CP-17 [REVISED — v2.9]

#### U-CP-17 — Implement workload-binding-time engine-class selection (5-step procedure) + declare `HITLInvocation` opener-side record (v2.9 — `HITLInvocation` specified as a faithful factor-out of C-CP-17 §17.1.1 `hitl_gate` argument set + C-CP-16 §16.4 + C-CP-20 §20.6)

[v2.1-introduced unit. **v2.9 factor-out delta.** T2 (`HITLInvocation` row) verdicts FACTOR-OUT — C-CP-17 §17 commits the HITL-invocation record; §16.4 `hitl.invocation.responded` event. v2.9 declares `HITLInvocation` at this unit (the HITL primitive unit per the T2 carrier assignment), cross-cluster-consumed by U-CP-52 via the existing `[U-CP-17]` edge (v2.6 §0.11.5). `HITLInvocation` is the *opener-side* record — distinct from the §17.1.1 `HITLResult`, which is the result-side record already concretely specified in the spec. All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-07 §7.3] (+ C-CP-17 §17.1.1 + C-CP-16 §16.4 + C-CP-20 §20.6 for the `HITLInvocation` factor-out)

**Depends on:** [U-CP-15, U-CP-16]

**Inputs:** `EngineClass` enum (U-CP-15); candidate mapping (U-CP-16). `HITLInvocation` consumes `HandoffContext` from U-CP-30 — within-axis edge; U-CP-30 is a prior-cluster unit, no new dependency edge created (the carrier-map edge already records U-CP-17 → handoff substrate).

**Files affected:** CP-axis workload-binding selection procedure (logical: `workload-binding-engine-class-selection`); CP-axis HITL invocation record (logical: `hitl-invocation-record`).

**Signatures:**

```
record WorkloadBindingSelectionInput {
  workload_class      : WorkloadClass
  deployment_surface  : DeploymentSurface
  persona_tier        : PersonaTier
  operator_preferences: Optional<EngineClassPreferences>
}

record WorkloadBindingSelectionResult {
  selected_class      : EngineClass
  candidate_set       : Set<EngineClass>
  selection_rationale : string
}

function select_engine_class(input: WorkloadBindingSelectionInput) -> WorkloadBindingSelectionResult

record HITLInvocation {
  invocation_id    : str
  placement        : str                       // ∈ {pre-action, sub-agent-boundary,
                                                //   validator-escalation} per C-CP-17 §17.1
  handoff_context  : HandoffContext             // per C-CP-13 §13.1 shape (U-CP-30)
  response_palette : Set<str>                   // {approve, edit, reject, respond} per C-CP-16 §16.1
  timeout          : Optional<Duration>         // None for sync-blocking; bounded for
                                                //   durable-async per C-CP-21 §21.3
  cascade_policy   : str                        // ∈ {pause, proceed, cascade-cancel} per C-CP-17 §17.1.1
  opened_at        : ISO8601                    // emission time of the hitl.invocation.opened event
}
// Opener-side record — the hitl.invocation.opened event payload (C-CP-20 §20.6 +
// C-CP-22 §22.3 reference `hitl.invocation.opened` with handoff_context_size_bytes).
// Field set is the C-CP-17 §17.1.1 `hitl_gate(...)` argument set + invocation_id +
// opened_at. DISTINCT from the §17.1.1 HITLResult (result-side record). No field
// invented beyond the §17.1.1 argument set.
```

**Acceptance criteria:**
1. `select_engine_class` implements §7.3 five-step procedure verbatim:
   - Step 1: Resolve candidate set from U-CP-16 per `deployment_surface`.
   - Step 2: Filter candidates by `workload_class` admissibility (event-sourced-replay favored at pipeline-automation; save-point-checkpoint favored at software-engineering; reconciler-loop favored at content-creation when reconvergence required).
   - Step 3: Filter candidates by `persona_tier` (solo-developer admits pure-pattern; team-binding+ requires durability primitive).
   - Step 4: Apply operator preferences if declared.
   - Step 5: Return single selected class; selection_rationale documents winning filter.
2. Selection is deterministic given inputs; no inference path.
3. Selection runs at **workload-binding time** (not at runtime); validation failure aborts workflow binding.
4. **`HITLInvocation` declares exactly seven fields — `invocation_id`, `placement`, `handoff_context`, `response_palette`, `timeout`, `cascade_policy`, `opened_at` — the C-CP-17 §17.1.1 `hitl_gate(...)` argument set plus `invocation_id` and `opened_at`.** `HITLInvocation` is the opener-side record, nominally distinct from the §17.1.1 `HITLResult`. No field invented beyond the §17.1.1 argument set; consumed cross-cluster by U-CP-52 via `[U-CP-17]`.

**Tests:** `test_select_engine_class_five_step`, `test_step_1_resolves_candidates_from_u_cp_16`, `test_step_2_workload_class_filter`, `test_step_3_persona_tier_filter`, `test_step_4_operator_preference_filter`, `test_selection_deterministic`, `test_selection_at_binding_time`, `test_hitl_invocation_seven_fields_cp_17_1_1`, `test_hitl_invocation_distinct_from_hitl_result`.

**Rollback boundary:** Revert workload-binding selection + `HITLInvocation` record. Workflow manifest entry (U-CP-13) loses engine-class binding source; manifest validation degrades to operator-declared engine without admissibility filtering; U-CP-52 loses the `HITLInvocation` carrier (cross-cluster `[U-CP-17]` edge dangles). A single coherent revert.

---

### §2A — U-CP-22 [REVISED — v2.9]

#### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate + `MaterialDiff` record (v2.9 — `MaterialDiff` specified as a faithful factor-out of C-CP-22 §22.2 material-diff detection contract + §22.1 diff-set tuple)

[v2.1-introduced unit; landed at the v2.8 batch is the topology portion (the §22.2 material-diff detection contract is the v2.9 factor-out target). **v2.9 factor-out delta.** T2 (`MaterialDiff` row, *decided*) verdicts FACTOR-OUT — C-CP-22 §22.2 commits the material-diff detection contract explicitly + §22.1 the diff-set tuple. v2.9 specifies `MaterialDiff`. Note: U-CP-22's `TopologyPattern` enum + admissibility predicate are preserved verbatim from the v2.5 body (landed); the v2.9 delta adds only the `MaterialDiff` record. `MaterialDiff` consumes `ExternalReference` from U-CP-30 (within-axis; U-CP-30 is a prior-cluster unit). All non-signature content otherwise preserved verbatim.]

**Implements:** [C-CP-10 §10.1, §10.2] (+ C-CP-22 §22.1, §22.2 for the `MaterialDiff` factor-out)

**Depends on:** [preserved verbatim from the v2.5 U-CP-22 body — `[U-CP-00]` edge materialized at v2.5]

**Inputs:** [preserved verbatim from the v2.5 U-CP-22 body.] `MaterialDiff` consumes `ExternalReference` (U-CP-30) — within-axis.

**Files affected:** [preserved verbatim from the v2.5 U-CP-22 body] + CP-axis material-diff record (logical: `material-diff-record`).

**Signatures:**

```
[ TopologyPattern enum + admissibility predicate — preserved verbatim from the
  landed v2.5 U-CP-22 body; not re-transcribed here. ]

record MaterialDiff {
  reference      : ExternalReference            // the diffed external reference (U-CP-30)
  prior_snapshot : bytes                        // snapshot captured at HITL pause-time
  current_value  : bytes                        // value refetched at HITL resume-time
  is_material    : bool                         // result of the §22.2 per-reference-class
                                                //   material-diff predicate
}
// Faithful factor-out of the C-CP-22 §22.1 diff-set tuple
// `diff_set.add((external_reference, prior_snapshot, current_value))` plus the
// `is_material` boolean the §22.2 per-reference-class predicate table produces.
// No field invented beyond the §22.1/§22.2 contract.
```

**Acceptance criteria:**
1. [`TopologyPattern` / admissibility-predicate acceptance criteria preserved verbatim from the landed v2.5 U-CP-22 body.]
2. **`MaterialDiff` declares exactly four fields — `reference: ExternalReference`, `prior_snapshot: bytes`, `current_value: bytes`, `is_material: bool` — a faithful factor-out of the C-CP-22 §22.1 diff-set tuple plus the §22.2 material-diff predicate result.** No field invented; `is_material` is the §22.2 per-reference-class predicate output (F2-ledger-entry / external-MCP-resource / filesystem-state / failed-attempts-history rows).

**Tests:** [`TopologyPattern` tests preserved verbatim from the landed v2.5 body] + `test_material_diff_four_fields_cp_22_2`, `test_material_diff_is_material_predicate_result`.

**Rollback boundary:** [`TopologyPattern` rollback preserved verbatim] + revert the `MaterialDiff` record — U-CP-49 context-revalidation diff-set composition loses its diff substrate. A single coherent revert.

---

### §2A — U-CP-30 [REVISED — v2.9]

#### U-CP-30 — Declare `HandoffContext` + `ProposedAction` + `StateSummary` + `LedgerEntryRef` family schemas (v2.9 — `ProposedAction`, `ActionKind`, `ActionPayload`, `FailedAttempt`, `Alternative`, `RetryHistory`, `StateSummary` all specified as faithful factor-outs of C-CP-13 §13.1/§13.4 + C-CP-16/§17 + C-CP-03 §3.5)

[v2.1-introduced unit; Root-cause-A blocked at the v2.8 batch — the `HandoffContext` family consumed name-only / comment-only structured types. **v2.9 factor-out delta.** T2 verdicts the whole family FACTOR-OUT: `HandoffContext`-family (*decided*), `ProposedAction`, `FailedAttempt`/`Alternative`/`RetryHistory` (*decided*), `CurrentState`(=`StateSummary`). v2.9 specifies all seven structured types; `ActionKind` is promoted from the v2.1 inline comment to a real enum (carrier-map line 113 *decided* promotion); `ActionPayload` is specified as the faithful opaque alias `Mapping[str, Any]` (NOT in T2 — §0.3.1, the `ProposedAction` committing sections §16/§17 do not decompose the payload). `CurrentState` is unified to `StateSummary` (already the canonical spelling). All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-13 §13.1, §13.4, §13.5] (+ C-CP-16 §16.1 + C-CP-17 §17.1 for `ProposedAction`/`ActionKind`; + C-CP-03 §3.5 for `FailedAttempt`/`RetryHistory`)

**Depends on:** [U-CP-07, U-CP-28, U-IS-07 (cross-axis: IS), U-IS-12 (cross-axis: IS)]

**Inputs:** `RETRY_NAMESPACE_SCHEMA` (U-CP-07) for `RetryHistory`; `SubAgentBrief` (U-CP-28); F2 entry shape (U-IS-07); idempotency-key join (U-IS-12).

**Files affected:** CP-axis HandoffContext schema (logical: `handoff-context-schema`); ProposedAction schema (logical: `proposed-action-schema`); StateSummary schema (logical: `state-summary-schema`); LedgerEntryRef schema (logical: `ledger-entry-ref-schema`); retry-history / failed-attempt records (logical: `retry-history-records`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `IDEMPOTENCY_KEY_JOIN_EXPORT` (C-IS-10 §10.1, §10.2 → U-IS-07, U-IS-12).

**Signatures:**

```
enum ActionKind {
  TOOL_CALL,            // tool-call action (C-CP-17 §17.1 pre-action placement trigger)
  SUB_AGENT_DISPATCH,   // parent→child handoff (C-CP-17 §17.1 sub-agent-boundary)
  INFERENCE_STEP        // inference-step action
}
// Closed at cardinality 3. Promotion of the v2.1 U-CP-30 inline comment
// `// {TOOL_CALL, SUB_AGENT_DISPATCH, INFERENCE_STEP}` to a real enum
// (carrier-map line 113 — DECIDED inline-comment-enum promotion). Values trace
// to the C-CP-17 §17.1 placement-trigger taxonomy + the C-CP-13 §13.1
// ProposedAction constituent.

type ActionPayload = Mapping[str, Any]
// Opaque alias. NOT a T2 candidate. The ProposedAction committing sections
// (C-CP-16 / §17) reference `edited_proposal` / `edited_proposal_hash` but do
// NOT decompose the action-payload field shape; §16.4 carries an explicit
// deferred clause. Faithful factor-out = the spec's own opaque vocabulary
// (cf. v2.8 ProviderAgnosticPayload sub-mappings). No field set invented.

record ProposedAction {
  action_kind : ActionKind
  payload     : ActionPayload
  brief       : Optional<SubAgentBrief>           // populated when action_kind = SUB_AGENT_DISPATCH
}
// Per C-CP-16 §16.1 four-response palette ("approve/edit/reject of a *proposed
// action*") + C-CP-17 §17 three-placement HITL primitive; ADR-D5 §1.1.

record FailedAttempt {
  attempt_index : int                            // ordinal of this failed attempt
  cause         : str                            // failure cause; joins retry.cause per C-CP-03 §3.5
  attempted_at  : ISO8601
}
// C-CP-13 §13.1 — HandoffContext.failed_attempts: List<FailedAttempt> "prior
// sub-agent failures on the same task"; cause vocabulary per C-CP-03 §3.5 retry.*.

record Alternative {
  description     : str                          // alternative the lead considered
  rejected_reason : str                          // why the lead did not take it
}
// C-CP-13 §13.1 — HandoffContext.alternatives_considered: List<Alternative>
// "lead's deliberation context".

record RetryHistory {
  attempts         : List<FailedAttempt>
  retry_count      : int
  last_retry_cause : Optional<str>               // joins retry.cause per C-CP-03 §3.5
}
// C-CP-13 §13.1 — RetryHistory NAMED in spec ("retry_history: RetryHistory —
// C9 retry primitives state per retry.* namespace at C-CP-03 §3.5"). FailedAttempt
// is its constituent. §13.4 defers the cardinality cap to implementation discretion.

record HandoffContext {
  proposed_action          : ProposedAction
  agent_confidence         : Optional<Float>
  failed_attempts          : List<FailedAttempt>
  alternatives_considered  : List<Alternative>
  state_summary            : StateSummary
  audit_trail_link         : LedgerEntryRef
  retry_history            : RetryHistory
}
// C-CP-13 §13.1 — seven fields verbatim.

record StateSummary {
  relevant_entries     : List<LedgerEntryRef>
  summary_text         : string
  summary_hash         : SHA256
  idempotency_key      : IdempotencyKey
  external_references  : List<ExternalReference>  // pause-time snapshot anchors per U-CP-49
}
// C-CP-13 §13.4 — committed by name and field-by-field. The CP audit's
// `CurrentState` is this concept under a plan spelling (T2 `CurrentState` row);
// v2.9 unifies the spelling to `StateSummary` (no `CurrentState` spelling reappears).

record LedgerEntryRef {
  action_id   : ActionID
  entry_hash  : SHA256                            // entry's response_hash per F2 entry shape
  actor       : ActorIdentity
}
// C-CP-13 §13.5 — three fields verbatim.

record ExternalReference {
  reference_class           : ReferenceClass      // {F2_LEDGER_ENTRY, EXTERNAL_MCP_RESOURCE,
                                                  //  FILESYSTEM_STATE, FAILED_ATTEMPTS_HISTORY}
  reference_id              : string
  snapshot_capture_at_pause : Optional<bytes>
}
// ReferenceClass value set per C-CP-22 §22.2 four-row material-diff reference-class table.
```

**Acceptance criteria:**
1. `HandoffContext` declares exactly seven fields per C-CP-13 §13.1 verbatim.
2. `StateSummary` declares five fields per §13.4 verbatim plus `external_references` for U-CP-49 pause-time snapshot composition. The CP audit's `CurrentState` spelling is unified to `StateSummary` — no `CurrentState` spelling appears.
3. `LedgerEntryRef` declares three fields per §13.5 verbatim.
4. `idempotency_key` references `IDEMPOTENCY_KEY_JOIN_EXPORT` per §13.4 + C-IS-10 §10.2.
5. T-perm-2 (across-turn boundary) crosses through F2 read/write contract pair per §13.1; F2-layer resolution stands.
6. Serialization format deferred to implementation discretion per spec §13.1 deferred list.
7. **`ActionKind` declares exactly three values `TOOL_CALL | SUB_AGENT_DISPATCH | INFERENCE_STEP`** — promotion of the v2.1 inline comment to a real enum (carrier-map line 113 decided). **`ProposedAction` declares exactly three fields `action_kind`, `payload`, `brief`** per C-CP-13 §13.1 + §16/§17. **`ActionPayload` is the opaque alias `Mapping[str, Any]`** — no field set invented (the §16/§17 committing sections do not decompose it).
8. **`FailedAttempt` declares three fields, `Alternative` declares two fields, `RetryHistory` declares three fields** — faithful factor-outs of C-CP-13 §13.1 (`failed_attempts` / `alternatives_considered` / `retry_history`) + the C-CP-03 §3.5 `retry.*` namespace. No field invented; the `RetryHistory` cardinality cap remains implementation-discretion per §13.4.

**Tests:** `test_handoff_context_seven_fields`, `test_state_summary_five_plus_external_refs`, `test_ledger_entry_ref_three_fields`, `test_idempotency_key_join_export`, `test_t_perm_2_f2_read_write`, `test_serialization_deferred`, `test_action_kind_cardinality_three`, `test_proposed_action_three_fields`, `test_action_payload_opaque_mapping_no_invented_fields`, `test_failed_attempt_three_fields`, `test_alternative_two_fields`, `test_retry_history_three_fields`, `test_no_current_state_spelling` (regression — the unified spelling holds).

**Rollback boundary:** Revert the `HandoffContext` family schemas. Sub-agent dispatch loses its payload contract; U-CP-13/14/38/50 lose the `HandoffContext` / `StateSummary` / `LedgerEntryRef` carrier; U-CP-22's `MaterialDiff` loses `ExternalReference`. A single coherent revert.

---

### §2A — U-CP-33 [REVISED — v2.9]

#### U-CP-33 — Implement concurrent-prompt-cache warm-up protocol + declare `LeadAgentPlan` (v2.9 — `LeadAgentPlan` specified as the faithful opaque alias `Mapping[str, Any]` per §0.5.2; the spec commits the concept but does not decompose a record)

[v2.1-introduced unit; Root-cause-C blocked at the v2.8 batch (`Depends on: [U-CP-32, …]` — U-CP-32 out of scope). **v2.9 factor-out delta.** T2 (`LeadAgentPlan` row) verdicts FACTOR-OUT — ADR-D4 v1.1 + C-CP-13 §13.3 commit the lead-agent role; C-CP-14 §14.4 step 1 commits "persist lead-agent's plan to filesystem". The spec commits the *concept* but does **not** characterize a `LeadAgentPlan` record shape — §13.2 characterizes the distinct `SubAgentBrief`, §14.4 is a procedure. Per the not-in-spec-decomposition discipline (§0.5.2): `LeadAgentPlan` is specified as the opaque alias `Mapping[str, Any]` — a faithful factor-out, NOT an invented `{plan_text, breakpoint_id, siblings}` record (the v2.1 body declared it name-only). U-CP-33 is unblocked. The Root-cause-C U-CP-32 dependency clears once U-CP-32 lands (transitive — outside v2.9 scope). All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-14 §14.4] (+ ADR-D4 v1.1 + C-CP-13 §13.3 for the `LeadAgentPlan` concept)

**Depends on:** [U-CP-32, U-AS-31 (cross-axis: AS), U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]

**Inputs:** Span hierarchy (U-CP-32); `anthropic.*` cache attributes (U-AS-31); filesystem path contract (U-IS-01); path-resolver (U-IS-02).

**Files affected:** CP-axis fan-out warm-up protocol (logical: `concurrent-prompt-cache-warmup`); CP-axis lead-agent-plan alias (logical: `lead-agent-plan-alias`).

**Cross-axis substrate consumed.** `SIX_ANTHROPIC_PRIMITIVE_ATTRIBUTE_NAMESPACE_EXPORT` (C-AS-16 §16.4 → U-AS-31); `FILESYSTEM_PATH_CONTRACT_EXPORT` (C-IS-10 §10.4 → U-IS-01, U-IS-02).

**Protocol (§14.4 four-step verbatim):**

```
Step 1. Persist lead-agent's plan to filesystem (CoALA episodic memory) via U-IS-02 resolver
Step 2. Dispatch siblings[0] synchronously to write cache at anthropic.cache_breakpoint_id
Step 3. Await CACHE_ACKNOWLEDGEMENT OR FIRST_TOKEN_EMISSION (whichever fires first)
Step 4. Dispatch siblings[1..N-1] concurrently with cache-hit on shared prefix
```

**Signatures:**

```
type LeadAgentPlan = Mapping[str, Any]
// Opaque alias. ADR-D4 v1.1 + C-CP-13 §13.3 commit the lead-agent role +
// brief-authoring binding; C-CP-14 §14.4 step 1 commits "persist lead-agent's
// plan to filesystem (CoALA episodic memory)". The spec commits the CONCEPT
// (a persisted lead-agent deliberation artifact) but does NOT decompose a
// LeadAgentPlan record (§13.2 characterizes the distinct SubAgentBrief; §14.4
// is a procedure). Faithful factor-out = opaque alias — NOT an invented record.
// The warm-up protocol consumes the plan as a persisted blob (no field access).

record CacheWarmupInput {
  siblings              : List<SubAgent>
  cache_breakpoint_id   : string
  lead_agent_plan       : LeadAgentPlan
}

enum CacheCompletionProxyKind { CACHE_ACKNOWLEDGEMENT, FIRST_TOKEN_EMISSION }

record CacheCompletionProxy {
  proxy_kind  : CacheCompletionProxyKind
  proxy_at_ms : int
}

function on_fanout_dispatch(input: CacheWarmupInput) -> CacheWarmupResult
function persist_lead_agent_plan(plan: LeadAgentPlan) -> FilesystemPath
function await_cache_completion(sibling: SubAgent) -> CacheCompletionProxy
```

**Acceptance criteria:**
1. `on_fanout_dispatch` executes the four steps in order per §14.4 verbatim; no step skipped or reordered.
2. Step 1 plan persistence delegates to U-IS-02 against U-IS-01 `PathClass` at canonical CoALA episodic memory location.
3. Step 2 first sibling dispatched synchronously with cache-write at `anthropic.cache_breakpoint_id`; `anthropic.cache_creation_input_tokens` populated per U-AS-31.
4. Step 3 completion proxy is whichever of `CACHE_ACKNOWLEDGEMENT` / `FIRST_TOKEN_EMISSION` fires first.
5. Step 4 remaining siblings dispatched concurrently; siblings observe cache-hit via `anthropic.cache_read_input_tokens` at 0.10× cost.
6. Cross-family fallback during fan-out loses cache state for that sibling per U-CP-32 acceptance.
7. **`LeadAgentPlan` is the opaque alias `Mapping[str, Any]`** — a faithful factor-out of the C-CP-14 §14.4 "persist lead-agent's plan" concept; no record field set is invented (the spec does not decompose a `LeadAgentPlan` record). `persist_lead_agent_plan` treats the plan as a persisted blob; `pyright` resolves the alias at all consumers.

**Tests:** `test_on_fanout_dispatch_four_steps_in_order`, `test_step_1_persists_via_u_is_02`, `test_step_2_synchronous_cache_write`, `test_step_3_first_of_two_signals`, `test_step_4_concurrent_after_completion`, `test_cache_read_tokens_populated_on_hit`, `test_cache_state_lost_cross_family`, `test_lead_agent_plan_opaque_mapping_no_invented_fields`.

**Rollback boundary:** Revert fan-out warm-up protocol + `LeadAgentPlan` alias. Multi-agent prompt-cache warm-up dissolves; fan-out siblings lose shared-prefix cache-hit. A single coherent revert.

---

### §2A — U-CP-41 [REVISED — v2.9]

#### U-CP-41 — Implement both-by-tier overlay + two-agent-observer meta-class + persona-tier-binding selection (v2.9 — `VerifierResult` + `OverlayResolution` specified as faithful factor-outs of C-CP-18 §18.3/§18.4; constituent enums `VerifierVerdict` / `OverlayOutcome` declared)

[v2.1-introduced unit; Root-cause-A-adjacent — `evaluate_both_by_tier_overlay` and `dispatch_two_agent_observer` return name-only `OverlayResolution` / `VerifierResult`. **v2.9 factor-out delta.** T2 (`VerifierResult` + `OverlayResolution` rows) verdicts both FACTOR-OUT — C-CP-18 §18.3 commits the both-by-tier per-tool overlay outcomes; §18.4 commits the two-agent-observer verifier-output concept. v2.9 specifies both records + their constituent enums. All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-18 §18.3, §18.4, §18.5]

**Depends on:** [U-CP-37, U-CP-40, U-CP-43, U-CP-47]

**Inputs:** HITL palette (U-CP-37); matrix cell (U-CP-40); 4-axis multiplicative rule + `_hitl_required` (U-CP-43); validator-fail taxonomy (U-CP-47).

**Files affected:** CP-axis both-by-tier overlay (logical: `hitl-both-by-tier-overlay`); two-agent-observer (logical: `hitl-two-agent-observer-meta-class`); persona-tier-binding selection (logical: `persona-tier-binding-selection`); CP-axis verifier/overlay result records (logical: `verifier-overlay-result-records`).

**Signatures:**

```
enum VerifierVerdict {
  AGREE,        // verifier agrees with the proposed action
  DISAGREE      // verifier disagrees — surfaces to operator palette per §18.4
}
// C-CP-18 §18.4 — "verifier agreement and disagreement both surface as inputs
// to the operator response palette". Closed at cardinality 2.

enum OverlayOutcome {
  AUTO_NO_GATE,            // auto-tier — no HITL gate invoked
  ASK_GATE_VIA_SYNCHRONY,  // ask-tier — cell synchrony delivers the gate
  DENY_STRUCTURAL_REJECT   // deny-tier — dispatch structurally rejected
}
// C-CP-18 §18.3 both-by-tier overlay — per-tool tier ∈ {auto, ask, deny}
// determines which actions invoke HITL gate. Closed at cardinality 3.

record VerifierResult {
  verifier_verdict     : VerifierVerdict
  validator_fail_class : Optional<str>           // ∈ C-CP-21 §21.5 validator.fail.class
                                                 //   5-value set when verifier emits a fail
  verifier_span_id     : str                     // subagent.span[verifier] id per C-CP-14 §14.1
}
// Faithful factor-out of the C-CP-18 §18.4 two-agent-observer meta-class:
// verdict (agree/disagree) + the optional validator.fail.* class the §18.4
// audit-composition row commits ("verifier output emits validator.fail.*
// span attributes per C-CP-21 §21.5") + the verifier span id.

record OverlayResolution {
  overlay_outcome   : OverlayOutcome
  gate_invoked      : bool                       // §18.3 audit-composition row
  palette_restricted: bool                       // true at DENY per C-CP-19 §19.4
}
// Faithful factor-out of the C-CP-18 §18.3 both-by-tier per-tool overlay —
// the three §18.3 outcomes + the gate-invoked / palette-restricted booleans
// the §18.3 audit-composition row and C-CP-19 §19.4 commit.

record BothByTierOverlay {
  scope               : string                  // §18.3 row 1 verbatim
  composition_rule    : string                  // §18.3 row 2 verbatim
  audit_composition   : string                  // §18.3 row 3 verbatim
}
const BOTH_BY_TIER_OVERLAY: BothByTierOverlay

record TwoAgentObserverMetaClass {
  trigger_condition          : string           // §18.4 row 1 verbatim
  composition_with_primary   : string           // §18.4 row 2 verbatim
  audit_composition          : string           // §18.4 row 3 verbatim
  applicable_cell_predicate  : Cell -> bool
}
const TWO_AGENT_OBSERVER: TwoAgentObserverMetaClass

record PersonaTierBindingSelectionInput {
  operator_persona_tier        : PersonaTier
  operator_deployment_surface  : DeploymentSurface
  operator_engine_choice       : EngineClass
  operator_workflow_class      : WorkloadClass
}

record PersonaTierBindingSelectionResult {
  resolved_cell                  : HITLMatrixCell
  composition_with_c_cp_19       : ReferenceToUnit    // U-CP-43
  composition_with_c_cp_20       : ReferenceToUnit    // U-CP-42
  composition_with_c_cp_21       : ReferenceToUnit    // U-CP-47
  composition_with_c_cp_22       : ReferenceToUnit    // U-CP-49
  binding_valid                  : bool
  rejection_reason               : Optional<string>
}

function evaluate_both_by_tier_overlay(tool_tier: ToolTier, cell: HITLMatrixCell) -> OverlayResolution
function dispatch_two_agent_observer(proposed_action: ProposedAction, blast_radius: BlastRadiusTier) -> VerifierResult
function compose_persona_tier_binding_selection(input: PersonaTierBindingSelectionInput) -> PersonaTierBindingSelectionResult
```

**Acceptance criteria:**
1. `BOTH_BY_TIER_OVERLAY` declares three properties per C-CP-18 §18.3 verbatim: per-tool `tier ∈ {auto, ask, deny}` annotation gates HITL invocation at any cell; overlay does NOT replace cell's primitive shape; auto-tier emits `tool.call` span only, ask-tier emits both `tool.call` and `hitl.gate.evaluated`.
2. `evaluate_both_by_tier_overlay` returns an `OverlayResolution`; the `overlay_outcome` is one of the three `OverlayOutcome` values per tool_tier: AUTO → `AUTO_NO_GATE`; ASK → `ASK_GATE_VIA_SYNCHRONY`; DENY → `DENY_STRUCTURAL_REJECT` with `palette_restricted = true` per C-CP-19 §19.4.
3. `TWO_AGENT_OBSERVER` declares three properties per §18.4: trigger condition is Tier-3+ blast-radius; verifier output composes with primary HITL gate at `validator-escalation` placement; verifier emits `subagent.span[verifier]` + `validator.fail.*` per U-CP-47.
4. `compose_persona_tier_binding_selection` implements §18.5 five-step procedure verbatim: operator declares persona tier + deployment surface + engine class + workflow class; cell lookup via U-CP-40; candidate selection from §18.1 evidence column; composition with U-CP-43 / U-CP-42 / U-CP-47 / U-CP-49 enforced at runtime.
5. **`VerifierResult` declares exactly three fields — `verifier_verdict: VerifierVerdict`, `validator_fail_class: Optional<str>`, `verifier_span_id: str` — a faithful factor-out of C-CP-18 §18.4.** `VerifierVerdict` is a 2-value enum (`AGREE | DISAGREE`); `validator_fail_class`, when present, is drawn from the C-CP-21 §21.5 5-value `validator.fail.class` set. No field invented.
6. **`OverlayResolution` declares exactly three fields — `overlay_outcome: OverlayOutcome`, `gate_invoked: bool`, `palette_restricted: bool` — a faithful factor-out of C-CP-18 §18.3.** `OverlayOutcome` is a 3-value enum. No field invented.

**Tests:** [v2.1 `both-by-tier` / `two-agent-observer` / `persona-tier-binding` tests preserved] + `test_verifier_result_three_fields_cp_18_4`, `test_verifier_verdict_cardinality_two`, `test_overlay_resolution_three_fields_cp_18_3`, `test_overlay_outcome_cardinality_three`, `test_verifier_fail_class_in_cp_21_5_set`.

**Rollback boundary:** Revert both-by-tier overlay + two-agent-observer + persona-tier-binding selection + the `VerifierResult` / `OverlayResolution` records. HITL overlay evaluation and pre-HITL verification dissolve. A single coherent revert.

---

### §2A — U-CP-52 [REVISED — v2.9]

#### U-CP-52 — Implement HITL timeout-degradation + webhook delivery semantics (v2.9 — `WebhookConfig` + `WebhookPayload` specified as faithful factor-outs of C-CP-18 §18.5 / C-CP-21 §21.8 idempotency-keyed webhook signal delivery)

[v2.1-introduced unit; Root-cause-A-adjacent — `deliver_webhook` consumes name-only `WebhookConfig` / `WebhookPayload`, and consumes `HITLInvocation` cross-cluster. **v2.9 factor-out delta.** T2 (`WebhookConfig` + `WebhookPayload` rows) verdicts both FACTOR-OUT — C-CP-21 §21.8 commits the idempotency-keyed webhook signal-delivery contract `(approval_id, idempotency_key)`. v2.9 specifies both records. `HITLInvocation` is consumed cross-cluster from U-CP-17 (v2.9-declared) via the existing `[U-CP-17]` edge (v2.6 §0.11.5). All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-21 §21.6] (+ C-CP-18 §18.5 + C-CP-21 §21.8 for the webhook factor-out)

**Depends on:** [U-CP-37, U-CP-38, U-CP-46, U-IS-07 (cross-axis: IS), U-IS-11 (cross-axis: IS)] (+ cross-cluster `[U-CP-17]` for `HITLInvocation` — pre-existing per v2.6 §0.11.5)

**Inputs:** HITL palette (U-CP-37); HITL placement + signature (U-CP-38); `hitl.*` + `audit.*` span schemas (U-CP-46); F2 append (U-IS-07, U-IS-11); `HITLInvocation` (U-CP-17, cross-cluster).

**Files affected:** CP-axis HITL timeout-degradation (logical: `hitl-timeout-degradation`); CP-axis webhook delivery semantics (logical: `hitl-webhook-delivery`); CP-axis webhook config/payload records (logical: `webhook-config-payload-records`).

**Cross-axis substrate consumed.** F2 substrate seams (U-IS-07, U-IS-11).

**Signatures:**

```
enum TimeoutDegradationKind {
  CONTINUE_AS_REJECT,                            // treat timeout as REJECT response
  ESCALATE_TO_REVIEW_BOARD,                      // raise gate level; second invocation
  ABORT_WORKFLOW                                 // terminal; no further attempts
}

record TimeoutDegradationPolicy {
  persona_tier            : PersonaTier
  default_kind            : TimeoutDegradationKind
  override_permitted      : bool
  audit_required          : bool                 // always true
}
const TIMEOUT_DEGRADATION_TABLE: List<TimeoutDegradationPolicy>  // exactly 3 entries

record WebhookConfig {
  webhook_id      : str
  endpoint_url    : str
  timeout         : Duration                     // per C-CP-17 §17.1.1 hitl_gate timeout
  degradation_mode: str                          // ∈ {fail-closed, escalate-secondary-channel}
                                                 //   per C-CP-21 §21.8 timeout-degradation table
}
// Faithful factor-out of the C-CP-18 §18.5 + C-CP-21 §21.8 webhook-ingress
// contract for durable-async cells. No field invented.

record WebhookPayload {
  approval_id      : str                         // §21.8 (approval_id, idempotency_key) pair
  idempotency_key  : IdempotencyKey              // §21.8 idempotency-keyed signal delivery
  gate_evaluation_ref : EntryID                  // ledger join key (U-CP-52 v2.1 WebhookDeliveryEvent)
  payload_body     : Mapping[str, Any]           // opaque — §21.8 defers idempotency-key
                                                 //   extraction from inbound payload
}
// Faithful factor-out of the C-CP-21 §21.8 contract: "(approval_id,
// idempotency_key) checked against the ledger before signal application".
// payload_body opaque per the §21.8 deferred clause. No field invented.

record WebhookDeliveryEvent {
  webhook_id           : string
  workflow_id          : WorkflowID
  gate_evaluation_ref  : EntryID
  payload_hash         : SHA256
  delivery_attempts    : int
  delivery_outcome     : WebhookDeliveryOutcome
}

enum WebhookDeliveryOutcome { DELIVERED, RETRY_PENDING, EXHAUSTED_AFTER_RETRIES }

function on_hitl_timeout(invocation: HITLInvocation, persona_tier: PersonaTier) -> TimeoutDegradationKind
function deliver_webhook(webhook: WebhookConfig, payload: WebhookPayload) -> WebhookDeliveryEvent
```

**Acceptance criteria:**
1. `TimeoutDegradationKind` declares exactly three values per C-CP-21 §21.6 verbatim.
2. `TIMEOUT_DEGRADATION_TABLE` declares per §21.6 verbatim:
   - `SOLO_DEVELOPER` → `CONTINUE_AS_REJECT`; override permitted
   - `TEAM_BINDING` → `ESCALATE_TO_REVIEW_BOARD`; override permitted
   - `MULTI_TENANT_COMPLIANCE` → `ABORT_WORKFLOW`; override prohibited (terminal)
3. `on_hitl_timeout` emits audit entry per U-CP-46 `audit.policy.*` attributes; F2 entry written via U-IS-07 + U-IS-11. `on_hitl_timeout` consumes a `HITLInvocation` (U-CP-17, cross-cluster `[U-CP-17]`).
4. Webhook delivery delegates retry mechanics to harness retry primitive (substrate-anchored at C9 per U-CP-07 substrate-authority note); per-webhook retry budget deferred to implementation discretion per spec §21.6.
5. Webhook payload signature: `payload_hash = sha256(canonicalize(payload))`; receiver verification deferred.
6. `WebhookDeliveryOutcome` cardinality bounded at three; `EXHAUSTED_AFTER_RETRIES` triggers `audit.policy.webhook_delivery_failed = true`.
7. Webhook delivery is **idempotent** — duplicate delivery on retry does not produce duplicate workflow side effects (receiver-side dedup by `gate_evaluation_ref` join).
8. **`WebhookConfig` declares exactly four fields — `webhook_id`, `endpoint_url`, `timeout`, `degradation_mode` — a faithful factor-out of C-CP-18 §18.5 / C-CP-21 §21.8.** **`WebhookPayload` declares exactly four fields — `approval_id`, `idempotency_key`, `gate_evaluation_ref`, `payload_body` — a faithful factor-out of the C-CP-21 §21.8 `(approval_id, idempotency_key)` idempotency-keyed delivery contract**; `payload_body` is opaque (`Mapping[str, Any]`) per the §21.8 deferred clause. No field invented in either record.

**Tests:** `test_timeout_degradation_three_kinds`, `test_timeout_degradation_table_three_entries`, `test_on_hitl_timeout_emits_audit`, `test_webhook_retry_delegated`, `test_webhook_payload_hash`, `test_webhook_delivery_outcome_three`, `test_webhook_delivery_idempotent`, `test_webhook_config_four_fields_cp_21_8`, `test_webhook_payload_four_fields_cp_21_8`, `test_webhook_payload_body_opaque_no_invented_fields`.

**Rollback boundary:** Revert HITL timeout-degradation + webhook delivery semantics + the `WebhookConfig` / `WebhookPayload` records. Durable-async-cell timeout handling and webhook signal delivery dissolve; cross-cluster `[U-CP-17]` edge for `HITLInvocation` releases. A single coherent revert.

---

## §11.1 CP auxiliary-type registry — v2.9 delta

The following Pattern-D tail rows are added/revised — each homed at its consuming carrier unit (multi-body delta; no new carrier unit), with the v2.9-specified shape and the byte-exact trace:

| Type | Kind | Carrier | Consuming units | Trace |
|---|---|---|---|---|
| `ActionKind` | enum (3) | U-CP-30 | U-CP-30 (`ProposedAction` constituent) | C-CP-17 §17.1 + carrier-map line 113 (decided promotion) |
| `ActionPayload` | type alias (opaque) | U-CP-30 | U-CP-30 (`ProposedAction` constituent) | C-CP-16/§17 — opaque per §16.4 deferred clause (NOT T2) |
| `ProposedAction` | record (3) | U-CP-30 | U-CP-30, U-CP-38, U-CP-41 | C-CP-13 §13.1 + C-CP-16 §16.1 + C-CP-17 §17 |
| `FailedAttempt` | record (3) | U-CP-30 | U-CP-30 (`HandoffContext`/`RetryHistory`) | C-CP-13 §13.1 + C-CP-03 §3.5 |
| `Alternative` | record (2) | U-CP-30 | U-CP-30 (`HandoffContext`) | C-CP-13 §13.1 |
| `RetryHistory` | record (3) | U-CP-30 | U-CP-30 (`HandoffContext`) | C-CP-13 §13.1 (named in spec) + C-CP-03 §3.5 |
| `StateSummary` | record (5) | U-CP-30 | U-CP-13, U-CP-14, U-CP-30, U-CP-49, U-CP-50 | C-CP-13 §13.4 (= the CP audit `CurrentState` — unified) |
| `RetryPolicy` | record (3) | U-CP-04 | U-CP-04 (`RoutingManifest`) | C-CP-03 §3 + §3.5 `retry.policy` |
| `CPAuditLedgerEntry` | record (8) | U-CP-14 | U-CP-14, U-CP-27, U-CP-44 | C-CP-16 §16.2 — CP-distinct name per §0.5.1 |
| `CPSignedAuditLedgerEntry` | record (`entry` + 5) | U-CP-14 | U-CP-44 | C-CP-20 §20.1 + §20.4 — CP-distinct name per §0.5.1 |
| `HITLInvocation` | record (7) | U-CP-17 | U-CP-17, U-CP-52 (cross-cluster `[U-CP-17]`) | C-CP-17 §17.1.1 + C-CP-16 §16.4 + C-CP-20 §20.6 |
| `LeadAgentPlan` | type alias (opaque) | U-CP-33 | U-CP-33 (`CacheWarmupInput`) | C-CP-14 §14.4 — opaque per §0.5.2 |
| `VerifierResult` | record (3) | U-CP-41 | U-CP-41 | C-CP-18 §18.4 |
| `OverlayResolution` | record (3) | U-CP-41 | U-CP-41 | C-CP-18 §18.3 |
| `VerifierVerdict` | enum (2) | U-CP-41 | U-CP-41 (`VerifierResult` constituent) | C-CP-18 §18.4 |
| `OverlayOutcome` | enum (3) | U-CP-41 | U-CP-41 (`OverlayResolution` constituent) | C-CP-18 §18.3 |
| `WebhookConfig` | record (4) | U-CP-52 | U-CP-52 | C-CP-18 §18.5 + C-CP-21 §21.8 |
| `WebhookPayload` | record (4) | U-CP-52 | U-CP-52 | C-CP-21 §21.8 |
| `MaterialDiff` | record (4) | U-CP-22 | U-CP-22, U-CP-49 | C-CP-22 §22.1 + §22.2 |

Two sub-records are **NOT** added to the registry — they stay Class 1 (§0.5):

| Type | Status | Reason |
|---|---|---|
| `RoleRoutingBinding` | 🛑 Class 1 | Not T2-covered; C-CP-06 §6.1 does not decompose it; field set uncommitted. `.harness/class_1_tension_role_routing_binding_underspec.md` filed. |
| `WorkloadRoutingOverride` | 🛑 Class 1 | Same — not T2-covered; uncommitted. |

`InferenceRequest` is **not** a registry row — it is unified to the v2.8 U-CP-00c `ProviderAgnosticPayload` (§0.1 item 3). All other §11.1 rows (the 9 U-CP-00c structured types, the U-CP-00b utility enums, the U-CP-08 `FallThroughCause`, the U-CP-11 `LeaseMechanism`/`LeaseReleaseCause`, the `harness-core` rows) are preserved verbatim from v2.8/v2.7/v2.6. Per §11.2 registry discipline, every Pattern-D tail row above now carries a reachable carrier — the second Pattern-D cluster is closed (modulo the two §0.5 sub-records); the affected consumer units (§0.6) may land.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_9.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-16 — v2.9 revision (Pattern-D tail structured-type specification — multi-body delta over 8 unit bodies) |
| Authoring authority | Operator ratification of the T2 X-AL-3 FACTOR-OUT resolution (`.harness/xal3_resolution_recommendations.md`) + operator task authorization 2026-05-16 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_8.md` (9 deferred structured types + U-CP-08 / U-CP-11 conformance) |
| Successor consumption | The 8 revised unit bodies (U-CP-04/14/17/22/30/33/41/52) and their Pattern-D-tail-dependent consumers land against this file; the 11 batch-blocked units are unblocked (modulo U-CP-04 partial-land — §0.5) |
| Revision policy | Canonical for the CP axis plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Control Plane v2.9. Multi-body delta over v2.8 — the 8 revised §2A unit bodies (U-CP-04/14/17/22/30/33/41/52) specifying the Pattern-D tail structured types, plus the §11.1 registry delta. NO new carrier unit. All other sections preserved verbatim from v2.8/v2.7/v2.6. Two sub-records (`RoleRoutingBinding`, `WorkloadRoutingOverride`) left Class 1 per §0.5.*
