# Class 1 Tension — U-CP-38 (unlanded `HandoffContext` dependency + Pattern D)

**Status:** ✅ CLOSED (verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — U-CP-38 landed at `harness-cp/src/harness_cp/hitl_placement.py` (3-placement HITL enum + `hitl_gate` signature + `HITLPlacement` per C-CP-17 §17.1/§17.1.1/§17.3); U-CP-30 `HandoffContext` landed at `handoff_context.py`; dependency satisfied. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

| Field | Value |
|---|---|
| Unit | U-CP-38 — Declare 3-placement enum + `hitl_gate(...)` interface signature + `HITLPlacement` workflow-definition schema |
| Sub-phase | 7b — CP axis-stream |
| Fork class | Class 1 (halt-execution — unsatisfied dependency + Pattern D undeclared types) |
| Filed | 2026-05-16 |
| Actor | phase-7-implementation |
| Disposition | **SKIPPED — HALT** — not landed |

## Defect

U-CP-38 (CP plan v2.1 §2.6, canonical-current body — preserved verbatim through
v2.4/v2.6) cannot be landed at sub-phase 7b Level 1: its declared dependency
graph is unsatisfied and its central `hitl_gate` signature consumes types no
landed unit declares.

### (A) Unsatisfied dependency — `HandoffContext` (U-CP-30, not landed)

U-CP-38 `Depends on: [U-CP-22, U-CP-30, U-CP-37]`. `Inputs:` names "`HandoffContext`
(U-CP-30)". The `hitl_gate` signature consumes it by type:

```
function hitl_gate(
  placement       : HITLPlacementKind,
  handoff_context : HandoffContext,          <-- U-CP-30 type
  response_palette: Set<HITLResponse>,
  timeout         : Optional<Duration>,
  cascade_policy  : CascadePolicy
) -> HITLResult
```

`HandoffContext` is declared by **U-CP-30** ("U-CP-30 — Declare `HandoffContext`
+ `StateSummary` + `LedgerEntryRef` schemas", CP plan v2.1 line 1541).
**U-CP-30 is NOT landed** — it is not in the Level-1 cluster and no
`harness_cp` module declares it (the sole occurrence in the source tree is a
docstring reference in `sub_agent_brief.py`, not a declaration). U-CP-38's
acceptance #3 requires the `hitl_gate` signature to match §17.1.1 verbatim with
its five parameters — the `handoff_context` parameter cannot be typed without
U-CP-30 landed. Landing U-CP-38 first would force either an invented
`HandoffContext` shape (X-AL-3 design extension) or a broken import.

`.harness/materializability_audit_cp_plan.md` row for U-CP-38 verdicts FORK on
exactly this shape: "`HITLResult` consumes undeclared `EntryID`; `hitl_gate`
consumes `HandoffContext` (U-CP-30 in-cone) ... §2.7.6 Class 1." The "in-cone"
phrasing presumes proper topological ordering; at the actual landed state
U-CP-30 has not landed, so the dependency is unsatisfied.

### (B) Pattern D undeclared types in `HITLResult`

```
record HITLResult {
  response                : HITLResponse        (U-CP-37 — landed, OK)
  edited_proposal         : Optional<ProposedAction>   <-- undeclared
  response_text           : Optional<string>
  timestamp               : ISO8601
  audit_ledger_entry_id   : EntryID             (harness-core — OK)
  response_summary_hash   : SHA256                     <-- undeclared primitive
}
```

`ProposedAction` is declared by no CP unit and is not among the operator-noted
9 deferred structured types — it is a genuinely-undeclared Pattern D type
(an AS-axis / cross-axis action-proposal shape). `SHA256` is a hashing
primitive given no concrete declaration in the plan. `HITLResult` is the
declared return type of `hitl_gate`; it cannot be materialized without these.

`HITLPlacementKind`, `HITL_PLACEMENT_TRIGGERS`, and `HITLPlacement` (acc #1,
#2, #6) ARE self-declared and would be materializable in isolation — but
`HITLPlacement.tool_filter : Optional<List<ToolName>>` consumes an undeclared
`ToolName` and `HITLPlacement.cascade_policy` is fine (U-CP-22 `CascadePolicy`
landed). The unit's spine (`hitl_gate` + `HITLResult`) is fully blocked.

## Resolution

**HALT U-CP-38. Not landed. Skipped — continue the axis stream.**

A partial-land split is not clean here: the materializable residue
(`HITLPlacementKind`, `HITL_PLACEMENT_TRIGGERS`) is a minority of the unit and
`HITLPlacement` itself depends on `ToolName`; the unit's defining surface — the
`hitl_gate` interface and `HITLResult` — is blocked on (A) + (B). Splitting
would leave a fragment that no downstream consumer can use without the gate
signature. The whole unit is deferred until U-CP-30 lands and the
`ProposedAction` / `ToolName` / `SHA256` types are resolved.

## Recommended back-flow

Two-part:

1. **Dependency ordering.** U-CP-38 must land *after* U-CP-30
   (`HandoffContext`). U-CP-30 is itself a FORK in the materializability audit
   (`LedgerEntryRef` consumes undeclared `ActorIdentity`). The CP plan's
   topological sort places U-CP-38 at Level 1, but U-CP-30 is not in the
   Level-1 cluster — the level assignment is inconsistent with the
   `handoff_context` consumption. A CP plan revision should reconcile the
   level assignment so U-CP-38 follows U-CP-30.
2. **Pattern D type residence (design-phase / CP plan revision).** The
   operator/architect must decide the carrier for `ProposedAction` (an
   action-proposal shape — likely an AS-axis or `harness-core` type) and
   `ToolName` (an identifier alias — `harness-core` identity-module candidate),
   and whether `SHA256` is a `str`-newtype hash alias. These are the same
   Pattern D structured-type residence calls tracked across the CP plan v2.4
   §4A cluster.

Until U-CP-30 lands and the Pattern D types are homed, U-CP-38 stays unlanded.
Downstream consumers: U-CP-39 (`Depends on: [U-CP-37, U-CP-38, ...]`) is
independently fork-blocked; U-CP-13 (`Depends on` includes U-CP-38) is not in
the Level-1 set. No landed unit regresses from this skip.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** U-CP-38 verified landed at harness-cp/src/harness_cp/hitl_placement.py (3-placement HITL enum + hitl_gate signature + HITLPlacement schema per C-CP-17 §17.1/§17.1.1/§17.3). U-CP-30 HandoffContext also landed at handoff_context.py. Dependency satisfied.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
