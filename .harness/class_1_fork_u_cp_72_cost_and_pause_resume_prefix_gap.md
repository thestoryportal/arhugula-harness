# Class 1 Fork — U-CP-72 cost + pause/resume prefix gap

**Filed:** 2026-05-22 at 10-CP-D cluster open (during `phase-7-implementation` skill §3.4 dependency-verification step for U-CP-72).

**Status:** OPEN (partial-land planned per `[[halt-route-split-AC-pattern]]` memory; 6 of 8 prefix branches materializable; 2 cross-axis-blocked).

**Trigger.** Implementation_Plan_Control_Plane_v2_15.md U-CP-72 AC #1 mandates routing for 8 action_id prefixes (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:`+`resume:` / `mcp_trust:` / `cost:`). AC #2 mandates each branch produces a correct AuditPayload subclass per OD spec.

Empirical inventory of AuditPayload subclasses at HEAD `5d67959`:

| Prefix | Required AuditPayload subclass | Status at HEAD |
|---|---|---|
| `dispatch:` | base `AuditPayload` (via `CPAuditLedgerEntry`) | landed |
| `hitl:` | base `AuditPayload` (via `CPAuditLedgerEntry`) | landed |
| `hitl_webhook:` | `WebhookDeliveryAuditPayload` | landed (U-OD-53, commit `0aed0ac`) |
| `operator_burden:` | `OperatorBurdenAuditPayload` | landed (U-OD-54, commit `128ab4f`) |
| `validator:` | `ValidatorEscalationAuditPayload` | landed (U-OD-50) |
| `mcp_trust:` | `TrustEvaluationAuditPayload` | landed (U-OD-52) |
| `pause:` / `resume:` | `PauseResumeAuditPayload` | **MISSING** — owed to U-OD-51 (cross-axis-blocked on U-CP-62 per OD plan v2.15 §1) |
| `cost:` | `CostRecordAuditPayload` | **MISSING** — owed to CXA v2.9 amendment (§2.3.7 row 8); paired with U-OD-41 producer per OD plan v2.14 §1 U-OD-41 AC #3 |

## §1 Decision class

**Class 1 — halt-route-split-AC.** Per workspace memory `[[halt-route-split-AC-pattern]]`: when a unit's AC bundles a materializable + unmaterializable surface, partial-land + strike the bad AC + file Class 1 fork.

## §2 Authority chain for the 2 missing surfaces

### §2.1 `pause:` / `resume:` — PauseResumeAuditPayload

- **Producer-side schema:** OD spec v1.9 §C-OD-30.1 + §C-OD-30.2 (8-attribute Pattern-P1 alignment with CP spec v1.11 §26.4 `WorkflowPauseReason` enum).
- **Producer unit:** U-OD-51 (OD plan v2.15) — pause/resume schema + PauseResumeAuditPayload dataclass.
- **Blocking dependency:** U-OD-51 cross-axis-blocked on U-CP-62 (CP plan v2.17 §1 — `WorkflowPauseReason` 5-class workflow-layer pause taxonomy materialization).
- **Routing target:** U-OD-51 + U-CP-62 implementation arc (separate from this 10-CP-D arc).

### §2.2 `cost:` — CostRecordAuditPayload

- **Producer-side schema:** owed to CXA v2.9 amendment per workspace `CLAUDE.md` §2.4 CXA row footer + handoff §6.
- **CXA amendment owed:** §2.3.7 row 8 (cost-attribution audit-write seam) per Implementation_Plan_Control_Plane_v2_15.md U-CP-72 cross-arc note: "AC #1 expansion from 7 → 8 prefixes requires CXA v2.6 → v2.7 amendment to add an §2.3.7 row 8 entry for cost-attribution audit-write seam."
- **Producer unit:** U-OD-41 (OD plan v2.14) — `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry`; current signature projects to `CPAuditLedgerEntry` (existing type), NOT a `CostRecordAuditPayload`. The producer-side spec contract for the new AuditPayload subclass is not yet authored.
- **Routing target:** CXA v2.9 amendment (canonicalizes the cost-attribution seam) + OD plan revision (CostRecordAuditPayload authoring) + U-OD-41 implementation arc.

## §3 Partial-land scope (this arc)

**U-CP-72 will land 6 of 8 prefix branches** in the `cp_audit_to_od_audit` converter:

1. `dispatch:` (via CPAuditLedgerEntry — preserved existing path)
2. `hitl:` (via CPAuditLedgerEntry — preserved existing path)
3. `hitl_webhook:` → `WebhookDeliveryAuditPayload`
4. `operator_burden:` → `OperatorBurdenAuditPayload`
5. `validator:` → `ValidatorEscalationAuditPayload`
6. `mcp_trust:` → `TrustEvaluationAuditPayload`

**Struck from this arc** (re-binding criterion explicit):

| Struck branch | Re-binding criterion |
|---|---|
| `pause:` / `resume:` → `PauseResumeAuditPayload` | U-OD-51 lands (waits on U-CP-62 per OD plan v2.15 §1 + checkpoint #4) |
| `cost:` → `CostRecordAuditPayload` | CXA v2.9 amendment authored + CostRecordAuditPayload subclass landed at OD package |

AC #1 modified at landing: `8 prefixes` → `6 prefixes`. AC #5 modified at landing: `8 producer events → 8 distinct AuditPayload subclasses` → `6 producer events → 6 distinct AuditPayload subclasses + base CPAuditLedgerEntry`.

## §4 Cross-axis impact

ZERO new cross-axis edges introduced by this fork resolution. The 6 landable branches consume existing producer-side AuditPayload subclasses (CP→CXA reverse-direction package imports already declared at CXA package per `harness-cxa/src/harness_cxa/cp_audit_conversion.py`). The 2 struck branches retain their original cross-axis dependency declarations at the plan body for future re-binding.

## §5 Non-amendment to U-CP-72 plan body at this arc

Per `[[halt-route-split-AC-pattern]]` discipline, the plan-body AC strikes are recorded at the landing commit message (commit body documents the strike + re-binding criterion); a CP plan v2.17 → v2.18 amendment is NOT owed at this arc (the strikes are bounded carry-forward, not contract changes). Future re-binding at the missing-subclass-landing arcs will un-strike via planner revision-pass naturally.

## §6 Adjacent finding — U-OD-41 signature precedes CostRecordAuditPayload authoring

OD plan v2.14 §1 U-OD-41 signature `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry` projects to the EXISTING `CPAuditLedgerEntry` type, not to a `CostRecordAuditPayload`. This is consistent with U-OD-41 AC #3 (`Routes via cp_audit_to_od_audit converter (action_id prefix cost: added per U-CP-72 extension — note: covered by cost: discriminator as the 8th pattern; reviewer to confirm bucket sizing or extend U-CP-72)`). The "reviewer to confirm" clause acknowledges the spec-level ambiguity; the CXA v2.9 amendment + OD plan revision authoring `CostRecordAuditPayload` is the canonical resolution path. Logged here for cross-reference at the CXA v2.9 amendment arc.

## §7 Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-22 |
| Filing arc | 10-CP-D cluster impl (U-CP-71 + U-CP-72 pair) |
| Filing skill | `phase-7-implementation` §3.4 dependency-verification |
| Resolution arc(s) | (a) U-OD-51 unblock at U-CP-62 landing; (b) CXA v2.9 amendment + CostRecordAuditPayload authoring |
| Status | OPEN at filing → PARTIAL-RESOLVED at U-CP-72 6-branch landing → FULLY-RESOLVED at re-binding arcs |
| Related memory | `[[halt-route-split-AC-pattern]]`, `[[carried-fork-audit-before-cluster]]` |
